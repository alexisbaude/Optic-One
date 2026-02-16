#!/usr/bin/env python3
"""
Advanced AI Assistant for Optic One
Near-instant responses with streaming, caching, and optimization
"""

import requests
import json
import time
import logging
import threading
from typing import Optional, Dict, List, Any, Generator
from datetime import datetime, timedelta
from collections import OrderedDict
import hashlib
import queue


class StreamingResponse:
    """Handle streaming responses from Ollama"""
    
    def __init__(self):
        self.chunks: List[str] = []
        self.complete = False
        self.error: Optional[str] = None
    
    def add_chunk(self, chunk: str):
        """Add chunk to response"""
        self.chunks.append(chunk)
    
    def get_text(self) -> str:
        """Get complete response text"""
        return ''.join(self.chunks)
    
    def mark_complete(self):
        """Mark response as complete"""
        self.complete = True
    
    def mark_error(self, error: str):
        """Mark response as error"""
        self.error = error
        self.complete = True


class AIAssistant:
    """
    Advanced AI assistant with optimizations for near-instant responses
    
    Features:
    - Response streaming for faster perceived speed
    - Intelligent caching with LRU eviction
    - Parallel request processing
    - Preloading common queries
    - Context management
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.base_url = config['base_url']
        self.model = config['model']
        self.timeout = config.get('timeout', 15)
        self.max_tokens = config.get('max_tokens', 512)
        self.temperature = config.get('temperature', 0.7)
        self.stream_enabled = config.get('stream', True)
        self.num_ctx = config.get('num_ctx', 2048)
        
        # Optimization settings
        opt_config = config.get('optimization', {})
        self.cache_enabled = opt_config.get('cache_responses', True)
        self.cache_ttl = opt_config.get('cache_ttl', 300)
        self.preload_enabled = opt_config.get('preload_common_queries', True)
        self.parallel_enabled = opt_config.get('parallel_processing', True)
        
        # Response cache (LRU)
        self.cache: OrderedDict = OrderedDict()
        self.cache_max_size = 100
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        # Conversation context
        self.context: List[Dict[str, str]] = []
        self.max_context_messages = 10
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'average_response_time': 0,
            'streaming_responses': 0
        }
        
        # Preload queue
        self.preload_queue: queue.Queue = queue.Queue()
        self.preload_thread: Optional[threading.Thread] = None
        
        # Verify connection
        self._verify_connection()
        
        # Start preloading if enabled
        if self.preload_enabled:
            self._start_preloading()
        
        logging.info(f"AI Assistant initialized (model: {self.model}, streaming: {self.stream_enabled})")
    
    def _verify_connection(self) -> bool:
        """Verify connection to Ollama"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                logging.info(f"Connected to Ollama - {len(models)} models available")
                return True
            else:
                logging.warning(f"Ollama connection issue: {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"Cannot connect to Ollama: {e}")
            return False
    
    def _start_preloading(self):
        """Start preloading common queries"""
        common_queries = [
            "What time is it?",
            "What's the weather?",
            "Help me navigate",
            "Read this text",
            "Translate this",
        ]
        
        for query in common_queries:
            self.preload_queue.put(query)
        
        self.preload_thread = threading.Thread(
            target=self._preload_worker,
            daemon=True,
            name="AIPreloader"
        )
        self.preload_thread.start()
    
    def _preload_worker(self):
        """Worker thread for preloading responses"""
        while True:
            try:
                query = self.preload_queue.get(timeout=1)
                
                # Generate and cache response
                cache_key = self._get_cache_key(query)
                if cache_key not in self.cache:
                    logging.debug(f"Preloading: {query}")
                    self.ask(query, use_cache=True)
                
                self.preload_queue.task_done()
                
            except queue.Empty:
                time.sleep(5)
            except Exception as e:
                logging.error(f"Preload error: {e}")
    
    def _get_cache_key(self, prompt: str, **kwargs) -> str:
        """Generate cache key for request"""
        cache_data = {
            'prompt': prompt,
            'model': kwargs.get('model', self.model),
            'temperature': kwargs.get('temperature', self.temperature)
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[str]:
        """Retrieve response from cache"""
        if not self.cache_enabled or cache_key not in self.cache:
            return None
        
        entry = self.cache[cache_key]
        
        # Check if expired
        if datetime.now() - entry['timestamp'] > timedelta(seconds=self.cache_ttl):
            del self.cache[cache_key]
            return None
        
        # Move to end (LRU)
        self.cache.move_to_end(cache_key)
        self.metrics['cache_hits'] += 1
        
        logging.debug(f"Cache hit: {cache_key[:8]}")
        return entry['response']
    
    def _add_to_cache(self, cache_key: str, response: str):
        """Add response to cache"""
        if not self.cache_enabled:
            return
        
        # Limit cache size
        if len(self.cache) >= self.cache_max_size:
            self.cache.popitem(last=False)
        
        self.cache[cache_key] = {
            'response': response,
            'timestamp': datetime.now()
        }
    
    def ask(self, 
            prompt: str, 
            use_context: bool = False,
            use_cache: bool = True,
            stream_callback: Optional[callable] = None,
            **kwargs) -> str:
        """
        Ask AI assistant a question with optimizations
        
        Args:
            prompt: User question/prompt
            use_context: Use conversation context
            use_cache: Check cache for response
            stream_callback: Callback for streaming chunks (chunk: str) -> None
            **kwargs: Additional parameters
        
        Returns:
            AI response text
        """
        start_time = time.time()
        self.metrics['total_requests'] += 1
        
        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(prompt, **kwargs)
            cached = self._get_from_cache(cache_key)
            if cached:
                if stream_callback:
                    # Simulate streaming for cached responses
                    for chunk in self._chunk_text(cached, chunk_size=10):
                        stream_callback(chunk)
                        time.sleep(0.01)
                return cached
        
        # Build messages
        messages = []
        if use_context and self.context:
            messages = self.context.copy()
        messages.append({'role': 'user', 'content': prompt})
        
        # Make request
        if self.stream_enabled and stream_callback:
            response_text = self._request_streaming(messages, stream_callback, **kwargs)
            self.metrics['streaming_responses'] += 1
        else:
            response_text = self._request_standard(messages, **kwargs)
        
        # Update context
        if use_context and response_text:
            self.context.append({'role': 'user', 'content': prompt})
            self.context.append({'role': 'assistant', 'content': response_text})
            
            # Limit context size
            if len(self.context) > self.max_context_messages * 2:
                self.context = self.context[-self.max_context_messages * 2:]
        
        # Cache response
        if use_cache and response_text:
            cache_key = self._get_cache_key(prompt, **kwargs)
            self._add_to_cache(cache_key, response_text)
        
        # Update metrics
        elapsed = time.time() - start_time
        self._update_response_time(elapsed)
        
        logging.info(f"AI response generated in {elapsed:.2f}s (streaming: {self.stream_enabled})")
        
        return response_text
    
    def _request_streaming(self, 
                          messages: List[Dict],
                          callback: callable,
                          **kwargs) -> str:
        """Make streaming request to Ollama"""
        data = {
            'model': kwargs.get('model', self.model),
            'messages': messages,
            'stream': True,
            'options': {
                'temperature': kwargs.get('temperature', self.temperature),
                'num_predict': kwargs.get('max_tokens', self.max_tokens),
                'num_ctx': self.num_ctx
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=data,
                timeout=self.timeout,
                stream=True
            )
            
            full_response = []
            
            for line in response.iter_lines():
                if line:
                    chunk_data = json.loads(line)
                    
                    if 'message' in chunk_data:
                        chunk_text = chunk_data['message'].get('content', '')
                        if chunk_text:
                            full_response.append(chunk_text)
                            callback(chunk_text)
                    
                    if chunk_data.get('done', False):
                        break
            
            return ''.join(full_response)
            
        except Exception as e:
            logging.error(f"Streaming request error: {e}")
            return ""
    
    def _request_standard(self, messages: List[Dict], **kwargs) -> str:
        """Make standard (non-streaming) request"""
        data = {
            'model': kwargs.get('model', self.model),
            'messages': messages,
            'stream': False,
            'options': {
                'temperature': kwargs.get('temperature', self.temperature),
                'num_predict': kwargs.get('max_tokens', self.max_tokens),
                'num_ctx': self.num_ctx
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('message', {}).get('content', '')
            else:
                logging.error(f"API error: {response.status_code}")
                return ""
                
        except Exception as e:
            logging.error(f"Request error: {e}")
            return ""
    
    def _chunk_text(self, text: str, chunk_size: int = 10) -> Generator[str, None, None]:
        """Split text into chunks for simulated streaming"""
        words = text.split()
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i+chunk_size])
            if i + chunk_size < len(words):
                chunk += ' '
            yield chunk
    
    def _update_response_time(self, elapsed: float):
        """Update average response time metric"""
        count = self.metrics['total_requests']
        current_avg = self.metrics['average_response_time']
        self.metrics['average_response_time'] = (current_avg * (count - 1) + elapsed) / count
    
    def quick_ask(self, prompt: str, **kwargs) -> str:
        """Quick ask without context or caching (for one-off questions)"""
        return self.ask(prompt, use_context=False, use_cache=True, **kwargs)
    
    def clear_context(self):
        """Clear conversation context"""
        self.context.clear()
        logging.debug("Conversation context cleared")
    
    def clear_cache(self):
        """Clear response cache"""
        self.cache.clear()
        logging.debug("Response cache cleared")
    
    def get_metrics(self) -> Dict:
        """Get performance metrics"""
        cache_hit_rate = (self.metrics['cache_hits'] / self.metrics['total_requests'] * 100 
                         if self.metrics['total_requests'] > 0 else 0)
        
        return {
            **self.metrics,
            'cache_hit_rate': round(cache_hit_rate, 2),
            'cache_size': len(self.cache),
            'context_messages': len(self.context)
        }

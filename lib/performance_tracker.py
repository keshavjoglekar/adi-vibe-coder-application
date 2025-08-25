"""
Performance Tracking - Comprehensive metrics and optimization monitoring
"""

import time
import json
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    name: str
    value: float
    unit: str
    timestamp: float
    context: Dict[str, Any]

@dataclass
class AgentPerformance:
    agent_name: str
    execution_time_ms: float
    token_usage: int
    cost_estimate: float
    confidence_score: float
    quality_metrics: Dict[str, float]
    cache_hits: int
    cache_misses: int

class PerformanceTracker:
    """Track and optimize AI agent system performance"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.agent_performances: List[AgentPerformance] = []
        self.cache_stats = defaultdict(int)
        self.start_times = {}
        self.session_stats = {
            "total_tokens": 0,
            "total_cost": 0.0,
            "total_execution_time": 0.0,
            "agents_executed": 0,
            "cache_hit_rate": 0.0
        }
    
    def start_timer(self, operation: str) -> str:
        """Start timing an operation"""
        timer_id = f"{operation}_{time.time()}"
        self.start_times[timer_id] = time.time()
        return timer_id
    
    def end_timer(self, timer_id: str, operation: str, context: Dict[str, Any] = None) -> float:
        """End timing and record metric"""
        if timer_id not in self.start_times:
            logger.warning(f"Timer {timer_id} not found")
            return 0.0
        
        duration = (time.time() - self.start_times[timer_id]) * 1000  # Convert to ms
        del self.start_times[timer_id]
        
        metric = PerformanceMetric(
            name=f"{operation}_duration",
            value=duration,
            unit="ms",
            timestamp=time.time(),
            context=context or {}
        )
        self.metrics.append(metric)
        
        return duration
    
    def record_agent_performance(self, performance: AgentPerformance):
        """Record comprehensive agent performance data"""
        self.agent_performances.append(performance)
        
        # Update session stats
        self.session_stats["total_tokens"] += performance.token_usage
        self.session_stats["total_cost"] += performance.cost_estimate
        self.session_stats["total_execution_time"] += performance.execution_time_ms
        self.session_stats["agents_executed"] += 1
        
        # Update cache stats
        total_cache_requests = performance.cache_hits + performance.cache_misses
        if total_cache_requests > 0:
            hit_rate = performance.cache_hits / total_cache_requests
            self.session_stats["cache_hit_rate"] = hit_rate
        
        logger.info(f"Agent {performance.agent_name} completed in {performance.execution_time_ms:.1f}ms")
    
    def record_metric(self, name: str, value: float, unit: str = "", context: Dict[str, Any] = None):
        """Record a custom performance metric"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=time.time(),
            context=context or {}
        )
        self.metrics.append(metric)
    
    def get_agent_stats(self, agent_name: str) -> Dict[str, Any]:
        """Get performance stats for a specific agent"""
        agent_performances = [p for p in self.agent_performances if p.agent_name == agent_name]
        
        if not agent_performances:
            return {"error": f"No performance data for {agent_name}"}
        
        latest = agent_performances[-1]
        
        return {
            "execution_time_ms": latest.execution_time_ms,
            "token_usage": latest.token_usage,
            "cost_estimate": latest.cost_estimate,
            "confidence_score": latest.confidence_score,
            "quality_metrics": latest.quality_metrics,
            "cache_efficiency": latest.cache_hits / (latest.cache_hits + latest.cache_misses) if (latest.cache_hits + latest.cache_misses) > 0 else 0
        }
    
    def get_system_performance(self) -> Dict[str, Any]:
        """Get overall system performance metrics"""
        if not self.agent_performances:
            return {"status": "No performance data available"}
        
        avg_confidence = sum(p.confidence_score for p in self.agent_performances) / len(self.agent_performances)
        
        # Speed benchmarks
        speed_metrics = {}
        for perf in self.agent_performances:
            speed_metrics[f"{perf.agent_name}_speed"] = f"{perf.execution_time_ms:.1f}ms"
        
        return {
            "total_execution_time": f"{self.session_stats['total_execution_time']:.1f}ms",
            "average_confidence": f"{avg_confidence:.1%}",
            "total_cost_estimate": f"${self.session_stats['total_cost']:.4f}",
            "total_tokens": self.session_stats['total_tokens'],
            "cache_hit_rate": f"{self.session_stats['cache_hit_rate']:.1%}",
            "agents_executed": self.session_stats['agents_executed'],
            "speed_breakdown": speed_metrics,
            "cost_per_agent": f"${self.session_stats['total_cost'] / max(1, self.session_stats['agents_executed']):.4f}"
        }
    
    def generate_performance_report(self) -> str:
        """Generate formatted performance report"""
        system_perf = self.get_system_performance()
        
        report = f"""# System Performance Report

## 🚀 Speed Metrics
- **Total Processing Time**: {system_perf.get('total_execution_time', 'N/A')}
- **Average Confidence**: {system_perf.get('average_confidence', 'N/A')}
- **Cache Hit Rate**: {system_perf.get('cache_hit_rate', 'N/A')}

## 💰 Cost Efficiency
- **Total Cost**: {system_perf.get('total_cost_estimate', 'N/A')}  
- **Cost per Agent**: {system_perf.get('cost_per_agent', 'N/A')}
- **Total Tokens**: {system_perf.get('total_tokens', 'N/A')}

## 🔧 Agent Breakdown
"""
        
        for agent_name in set(p.agent_name for p in self.agent_performances):
            stats = self.get_agent_stats(agent_name)
            report += f"""
### {agent_name}
- Execution Time: {stats.get('execution_time_ms', 0):.1f}ms
- Confidence: {stats.get('confidence_score', 0):.1%}
- Token Usage: {stats.get('token_usage', 0)}
- Cache Efficiency: {stats.get('cache_efficiency', 0):.1%}
"""
        
        return report
    
    def save_performance_data(self, filepath: str):
        """Save performance data to file"""
        data = {
            "session_stats": self.session_stats,
            "agent_performances": [asdict(p) for p in self.agent_performances],
            "metrics": [asdict(m) for m in self.metrics],
            "timestamp": time.time()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Performance data saved to {filepath}")

# Global performance tracker
perf_tracker = PerformanceTracker()

# Performance monitoring decorators
def track_performance(agent_name: str):
    """Decorator to track agent performance"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            timer_id = perf_tracker.start_timer(f"{agent_name}_execution")
            
            try:
                result = await func(*args, **kwargs)
                
                # Extract performance data from result if available
                execution_time = perf_tracker.end_timer(timer_id, f"{agent_name}_execution")
                
                # Create performance record
                performance = AgentPerformance(
                    agent_name=agent_name,
                    execution_time_ms=execution_time,
                    token_usage=getattr(result, 'token_usage', 0),
                    cost_estimate=getattr(result, 'cost_estimate', 0.0),
                    confidence_score=getattr(result, 'confidence_score', 0.8),
                    quality_metrics=getattr(result, 'quality_metrics', {}),
                    cache_hits=getattr(result, 'cache_hits', 0),
                    cache_misses=getattr(result, 'cache_misses', 0)
                )
                
                perf_tracker.record_agent_performance(performance)
                
                return result
                
            except Exception as e:
                perf_tracker.end_timer(timer_id, f"{agent_name}_execution_failed")
                raise
        
        return wrapper
    return decorator

def benchmark_speed(operation_name: str):
    """Decorator for speed benchmarking"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            
            perf_tracker.record_metric(
                name=f"{operation_name}_speed",
                value=duration,
                unit="ms",
                context={"function": func.__name__}
            )
            
            return result
        return wrapper
    return decorator
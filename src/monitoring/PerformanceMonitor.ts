import * as Sentry from 'sentry-expo';
import { Performance } from 'expo-performance';

export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: Map<string, number> = new Map();
  private traces: Map<string, Sentry.Span> = new Map();

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  // Start performance measurement
  startTrace(name: string, operation: string): void {
    try {
      const span = Sentry.startSpan({
        op: operation,
        name: name,
      });
      
      if (span) {
        this.traces.set(name, span);
        console.log(`🚀 Performance trace started: ${name}`);
      }
    } catch (error) {
      console.warn('Performance monitoring not available:', error);
    }
  }

  // End performance measurement
  endTrace(name: string, status: 'ok' | 'error' = 'ok'): void {
    try {
      const span = this.traces.get(name);
      if (span) {
        span.setStatus(status);
        span.finish();
        this.traces.delete(name);
        console.log(`✅ Performance trace ended: ${name}`);
      }
    } catch (error) {
      console.warn('Performance monitoring not available:', error);
    }
  }

  // Measure function execution time
  async measureAsync<T>(
    name: string, 
    operation: () => Promise<T>,
    operationName: string = 'function'
  ): Promise<T> {
    const startTime = Date.now();
    this.startTrace(name, operationName);
    
    try {
      const result = await operation();
      const duration = Date.now() - startTime;
      this.metrics.set(name, duration);
      this.endTrace(name, 'ok');
      
      // Log performance metrics
      if (duration > 1000) {
        console.warn(`⚠️ Slow operation detected: ${name} took ${duration}ms`);
        Sentry.addBreadcrumb({
          category: 'performance',
          message: `Slow operation: ${name}`,
          level: 'warning',
          data: { duration, operation: operationName },
        });
      }
      
      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      this.metrics.set(name, duration);
      this.endTrace(name, 'error');
      
      // Report performance errors
      Sentry.addBreadcrumb({
        category: 'performance',
        message: `Operation failed: ${name}`,
        level: 'error',
        data: { duration, operation: operationName, error: error.message },
      });
      
      throw error;
    }
  }

  // Measure synchronous function execution time
  measureSync<T>(
    name: string, 
    operation: () => T,
    operationName: string = 'function'
  ): T {
    const startTime = Date.now();
    this.startTrace(name, operationName);
    
    try {
      const result = operation();
      const duration = Date.now() - startTime;
      this.metrics.set(name, duration);
      this.endTrace(name, 'ok');
      
      // Log performance metrics
      if (duration > 100) {
        console.warn(`⚠️ Slow sync operation: ${name} took ${duration}ms`);
        Sentry.addBreadcrumb({
          category: 'performance',
          message: `Slow sync operation: ${name}`,
          level: 'warning',
          data: { duration, operation: operationName },
        });
      }
      
      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      this.metrics.set(name, duration);
      this.endTrace(name, 'error');
      
      // Report performance errors
      Sentry.addBreadcrumb({
        category: 'performance',
        message: `Sync operation failed: ${name}`,
        level: 'error',
        data: { duration, operation: operationName, error: error.message },
      });
      
      throw error;
    }
  }

  // Track screen load time
  trackScreenLoad(screenName: string): void {
    this.startTrace(`screen_load_${screenName}`, 'navigation');
    
    // Auto-end trace after a reasonable time
    setTimeout(() => {
      this.endTrace(`screen_load_${screenName}`, 'ok');
    }, 5000);
  }

  // Track API call performance
  trackAPICall(endpoint: string, method: string): void {
    const name = `api_${method}_${endpoint}`;
    this.startTrace(name, 'http');
    
    // Auto-end trace after a reasonable time
    setTimeout(() => {
      this.endTrace(name, 'ok');
    }, 30000); // 30 seconds timeout
  }

  // Get performance metrics
  getMetrics(): Record<string, number> {
    return Object.fromEntries(this.metrics);
  }

  // Clear metrics
  clearMetrics(): void {
    this.metrics.clear();
  }

  // Report custom metric
  reportMetric(name: string, value: number, tags?: Record<string, string>): void {
    try {
      Sentry.metrics.increment(name, value, tags);
      this.metrics.set(name, value);
    } catch (error) {
      console.warn('Metrics reporting not available:', error);
    }
  }

  // Report error with context
  reportError(error: Error, context?: Record<string, any>): void {
    try {
      Sentry.Native.captureException(error, {
        extra: context,
        tags: {
          source: 'performance_monitor',
        },
      });
    } catch (sentryError) {
      console.error('Failed to report to Sentry:', sentryError);
      console.error('Original error:', error);
    }
  }
}

// Convenience functions
export const performance = PerformanceMonitor.getInstance();

// Performance decorators for easy use
export function measureAsync(name: string, operationName?: string) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = async function (...args: any[]) {
      return performance.measureAsync(
        `${target.constructor.name}.${propertyKey}`,
        () => originalMethod.apply(this, args),
        operationName || propertyKey
      );
    };
    
    return descriptor;
  };
}

export function measureSync(name: string, operationName?: string) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;
    
    descriptor.value = function (...args: any[]) {
      return performance.measureSync(
        `${target.constructor.name}.${propertyKey}`,
        () => originalMethod.apply(this, args),
        operationName || propertyKey
      );
    };
    
    return descriptor;
  };
}

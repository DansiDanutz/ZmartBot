import * as Sentry from 'sentry-expo';

export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: Map<string, number> = new Map();
  private traces: Map<string, any> = new Map();

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  // Start performance measurement
  startTrace(name: string, operation: string): void {
    try {
      // Store trace information for performance tracking
      this.traces.set(name, { name, operation, startTime: Date.now() });
      console.log(`🚀 Performance trace started: ${name}`);
    } catch (error) {
      console.warn('Performance monitoring not available:', error);
    }
  }

  // End performance measurement
  endTrace(name: string, status: 'ok' | 'error' = 'ok'): void {
    try {
      const trace = this.traces.get(name);
      if (trace) {
        const duration = Date.now() - trace.startTime;
        this.metrics.set(name, duration);
        this.traces.delete(name);
        console.log(`✅ Performance trace ended: ${name} (${duration}ms)`);
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
      }
      
      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      this.metrics.set(name, duration);
      this.endTrace(name, 'error');
      
      // Report performance errors
      console.error(`❌ Operation failed: ${name}`, error);
      
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
      }
      
      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      this.metrics.set(name, duration);
      this.endTrace(name, 'error');
      
      // Report performance errors
      console.error(`❌ Sync operation failed: ${name}`, error);
      
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
      this.metrics.set(name, value);
      console.log(`📊 Metric reported: ${name} = ${value}`, tags);
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

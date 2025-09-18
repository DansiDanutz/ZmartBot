/**
 * BASE AGENT CLASS
 * Foundation for all brain management sub-agents
 */

import EventEmitter from 'events';
import { createClient } from '@supabase/supabase-js';
import cron from 'node-cron';

export default class BaseAgent extends EventEmitter {
  constructor(config) {
    super();

    this.config = {
      name: 'BaseAgent',
      priority: 5,
      responsibilities: [],
      schedule: null,
      maxConcurrency: 3,
      retryAttempts: 3,
      ...config
    };

    // Agent state
    this.state = {
      status: 'idle',
      isRunning: false,
      currentTasks: new Set(),
      completedTasks: 0,
      failedTasks: 0,
      lastRun: null,
      health: 'healthy'
    };

    // Supabase client
    this.supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_ANON_KEY
    );

    // Message bus for inter-agent communication
    this.messageBus = null;

    // Task queue
    this.taskQueue = [];

    // Cron job
    this.cronJob = null;

    // Performance metrics
    this.metrics = {
      totalExecutions: 0,
      successfulExecutions: 0,
      failedExecutions: 0,
      avgExecutionTime: 0,
      lastExecutionTime: null
    };
  }

  /**
   * Set message bus for inter-agent communication
   */
  setMessageBus(messageBus) {
    this.messageBus = messageBus;
    this.setupMessageHandlers();
  }

  /**
   * Setup message handlers (to be overridden by child classes)
   */
  setupMessageHandlers() {
    // Override in child classes
  }

  /**
   * Start the agent
   */
  async start() {
    if (this.state.isRunning) return;

    this.state.isRunning = true;
    this.state.status = 'active';

    console.log(`🤖 Starting ${this.config.name}`);

    // Setup scheduled tasks
    if (this.config.schedule) {
      this.setupSchedule();
    }

    // Run initialization
    await this.initialize();

    // Start processing loop
    this.startProcessingLoop();

    this.emit('started', { agent: this.config.name });
  }

  /**
   * Stop the agent
   */
  async stop() {
    this.state.isRunning = false;
    this.state.status = 'stopped';

    // Stop cron job
    if (this.cronJob) {
      this.cronJob.stop();
    }

    // Wait for current tasks to complete
    await this.waitForTasks();

    console.log(`🛑 Stopped ${this.config.name}`);
    this.emit('stopped', { agent: this.config.name });
  }

  /**
   * Initialize agent (override in child classes)
   */
  async initialize() {
    // Override in child classes
  }

  /**
   * Setup scheduled execution
   */
  setupSchedule() {
    if (!this.config.schedule) return;

    this.cronJob = cron.schedule(this.config.schedule, async () => {
      await this.scheduledExecution();
    });
  }

  /**
   * Scheduled execution handler
   */
  async scheduledExecution() {
    try {
      this.state.lastRun = Date.now();
      await this.executeScheduledTasks();
    } catch (error) {
      this.handleError('Scheduled execution failed', error);
    }
  }

  /**
   * Execute scheduled tasks (override in child classes)
   */
  async executeScheduledTasks() {
    // Override in child classes
  }

  /**
   * Start processing loop
   */
  startProcessingLoop() {
    setInterval(async () => {
      if (!this.state.isRunning) return;
      await this.processQueue();
    }, 1000);
  }

  /**
   * Process task queue
   */
  async processQueue() {
    while (
      this.taskQueue.length > 0 &&
      this.state.currentTasks.size < this.config.maxConcurrency
    ) {
      const task = this.taskQueue.shift();
      this.processTask(task);
    }
  }

  /**
   * Process individual task
   */
  async processTask(task) {
    const taskId = task.id || crypto.randomUUID();
    this.state.currentTasks.add(taskId);

    const startTime = Date.now();

    try {
      // Execute task
      const result = await this.executeTask(task);

      // Update metrics
      this.updateMetrics(true, Date.now() - startTime);

      // Emit success
      this.emit('taskComplete', {
        taskId,
        result,
        duration: Date.now() - startTime
      });

      this.state.completedTasks++;

    } catch (error) {
      // Handle failure
      this.updateMetrics(false, Date.now() - startTime);

      if (task.retryCount < this.config.retryAttempts) {
        // Retry task
        this.queueTask({
          ...task,
          retryCount: (task.retryCount || 0) + 1
        });
      } else {
        // Final failure
        this.emit('taskFailed', {
          taskId,
          error,
          duration: Date.now() - startTime
        });

        this.state.failedTasks++;
      }
    } finally {
      this.state.currentTasks.delete(taskId);
    }
  }

  /**
   * Execute task (override in child classes)
   */
  async executeTask(task) {
    throw new Error('executeTask must be implemented by child class');
  }

  /**
   * Queue a task
   */
  queueTask(task) {
    this.taskQueue.push({
      id: crypto.randomUUID(),
      timestamp: Date.now(),
      retryCount: 0,
      ...task
    });
  }

  /**
   * Get agent health
   */
  async getHealth() {
    const health = {
      status: this.state.health,
      metrics: this.metrics,
      queueLength: this.taskQueue.length,
      activeTasks: this.state.currentTasks.size,
      lastRun: this.state.lastRun
    };

    // Check for issues
    if (this.state.failedTasks > this.state.completedTasks * 0.5) {
      health.status = 'degraded';
      health.issue = 'High failure rate';
    }

    if (this.taskQueue.length > 100) {
      health.status = 'degraded';
      health.issue = 'Queue backlog';
    }

    if (!this.state.lastRun || Date.now() - this.state.lastRun > 3600000) {
      health.status = 'warning';
      health.issue = 'No recent execution';
    }

    return health;
  }

  /**
   * Get current workload percentage
   */
  async getWorkload() {
    const maxLoad = this.config.maxConcurrency * 10; // Assume 10 tasks per slot is max
    const currentLoad = this.state.currentTasks.size + this.taskQueue.length;
    return Math.min(100, (currentLoad / maxLoad) * 100);
  }

  /**
   * Get redistributable tasks
   */
  async getRedistributableTasks() {
    // Return tasks that can be moved to other agents
    return this.taskQueue.slice(0, Math.floor(this.taskQueue.length / 2));
  }

  /**
   * Get agent status
   */
  getStatus() {
    return {
      status: this.state.status,
      health: this.state.health,
      activeTasks: this.state.currentTasks.size,
      queuedTasks: this.taskQueue.length,
      completedTasks: this.state.completedTasks,
      failedTasks: this.state.failedTasks,
      lastRun: this.state.lastRun
    };
  }

  /**
   * Check for pending dependencies
   */
  hasPendingDependencies() {
    // Override in child classes if agent has dependencies
    return false;
  }

  /**
   * Update metrics
   */
  updateMetrics(success, duration) {
    this.metrics.totalExecutions++;

    if (success) {
      this.metrics.successfulExecutions++;
    } else {
      this.metrics.failedExecutions++;
    }

    // Update average execution time (exponential moving average)
    const alpha = 0.1;
    this.metrics.avgExecutionTime =
      alpha * duration + (1 - alpha) * this.metrics.avgExecutionTime;

    this.metrics.lastExecutionTime = duration;
  }

  /**
   * Wait for all current tasks to complete
   */
  async waitForTasks() {
    const maxWait = 30000; // 30 seconds max
    const startTime = Date.now();

    while (
      this.state.currentTasks.size > 0 &&
      Date.now() - startTime < maxWait
    ) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    if (this.state.currentTasks.size > 0) {
      console.warn(`⚠️ ${this.config.name} stopped with ${this.state.currentTasks.size} active tasks`);
    }
  }

  /**
   * Handle errors
   */
  handleError(message, error) {
    console.error(`❌ ${this.config.name}: ${message}`, error);
    this.emit('error', { message, error });
  }

  /**
   * Log agent activity
   */
  async logActivity(activity, metadata = {}) {
    try {
      await this.supabase.from('brain_agent_logs').insert({
        agent_name: this.config.name,
        activity,
        metadata,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Failed to log activity:', error);
    }
  }

  /**
   * Send message to other agents
   */
  sendMessage(event, data) {
    if (this.messageBus) {
      this.messageBus.emit(event, {
        source: this.config.name,
        timestamp: Date.now(),
        ...data
      });
    }
  }

  /**
   * Execute a specific task (called by orchestrator)
   */
  async execute(task) {
    return await this.executeTask(task);
  }
}
/**
 * BRAIN SUB-AGENTS ORCHESTRATOR
 * Master coordinator for all specialized brain management sub-agents
 * Each agent has specific responsibilities for maintaining brain health and intelligence
 */

import EventEmitter from 'events';
import { createClient } from '@supabase/supabase-js';

// Import all sub-agents
import KnowledgeValidatorAgent from './agents/KnowledgeValidatorAgent.js';
import PatternDiscoveryAgent from './agents/PatternDiscoveryAgent.js';
import HistoryAnalyzerAgent from './agents/HistoryAnalyzerAgent.js';
import DataDistributorAgent from './agents/DataDistributorAgent.js';
import MemoryConsolidationAgent from './agents/MemoryConsolidationAgent.js';
import QualityControlAgent from './agents/QualityControlAgent.js';
import EvolutionOptimizerAgent from './agents/EvolutionOptimizerAgent.js';
import SemanticAnalyzerAgent from './agents/SemanticAnalyzerAgent.js';
import RelationshipMapperAgent from './agents/RelationshipMapperAgent.js';
import CacheOptimizerAgent from './agents/CacheOptimizerAgent.js';
import UserBehaviorAgent from './agents/UserBehaviorAgent.js';
import MarketIntelligenceAgent from './agents/MarketIntelligenceAgent.js';
import LearningPipelineAgent from './agents/LearningPipelineAgent.js';
import ConflictResolverAgent from './agents/ConflictResolverAgent.js';
import ArchiveManagerAgent from './agents/ArchiveManagerAgent.js';

class BrainSubAgentsOrchestrator extends EventEmitter {
  constructor() {
    super();

    // Initialize Supabase
    this.supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_ANON_KEY
    );

    // Agent registry
    this.agents = new Map();

    // Agent communication bus
    this.messageBus = new EventEmitter();

    // Orchestration state
    this.state = {
      isRunning: false,
      activeAgents: new Set(),
      queuedTasks: [],
      completedTasks: [],
      metrics: {
        totalTasks: 0,
        completedTasks: 0,
        failedTasks: 0,
        avgProcessingTime: 0
      }
    };

    // Initialize all agents
    this.initializeAgents();
  }

  /**
   * Initialize all sub-agents with their configurations
   */
  async initializeAgents() {
    console.log('🧠 Initializing Brain Sub-Agents...');

    // CORE VALIDATION AGENTS
    this.registerAgent('validator', new KnowledgeValidatorAgent({
      name: 'Knowledge Validator',
      priority: 10,
      responsibilities: [
        'Validate incoming knowledge for accuracy',
        'Check for duplicates and conflicts',
        'Verify source credibility',
        'Assign confidence scores'
      ],
      schedule: '*/5 * * * *' // Every 5 minutes
    }));

    this.registerAgent('qualityControl', new QualityControlAgent({
      name: 'Quality Control',
      priority: 9,
      responsibilities: [
        'Remove bad or outdated data',
        'Flag inconsistencies',
        'Maintain data quality standards',
        'Generate quality reports'
      ],
      schedule: '*/10 * * * *' // Every 10 minutes
    }));

    // DISCOVERY & LEARNING AGENTS
    this.registerAgent('patternDiscovery', new PatternDiscoveryAgent({
      name: 'Pattern Discovery',
      priority: 8,
      responsibilities: [
        'Identify new patterns in data',
        'Correlate user behaviors',
        'Discover market patterns',
        'Extract trading signals'
      ],
      schedule: '*/15 * * * *' // Every 15 minutes
    }));

    this.registerAgent('learningPipeline', new LearningPipelineAgent({
      name: 'Learning Pipeline',
      priority: 8,
      responsibilities: [
        'Process learning queue',
        'Convert discoveries to knowledge',
        'Update knowledge base',
        'Track learning progress'
      ],
      schedule: '*/10 * * * *' // Every 10 minutes
    }));

    // HISTORY & ANALYSIS AGENTS
    this.registerAgent('historyAnalyzer', new HistoryAnalyzerAgent({
      name: 'History Analyzer',
      priority: 7,
      responsibilities: [
        'Analyze historical patterns',
        'Track knowledge evolution',
        'Identify successful strategies',
        'Learn from failures'
      ],
      schedule: '0 * * * *' // Every hour
    }));

    this.registerAgent('userBehavior', new UserBehaviorAgent({
      name: 'User Behavior Analyzer',
      priority: 7,
      responsibilities: [
        'Track user interactions',
        'Identify user preferences',
        'Cluster user groups',
        'Personalize responses'
      ],
      schedule: '*/30 * * * *' // Every 30 minutes
    }));

    // DISTRIBUTION & ORGANIZATION AGENTS
    this.registerAgent('dataDistributor', new DataDistributorAgent({
      name: 'Data Distributor',
      priority: 8,
      responsibilities: [
        'Route knowledge to correct categories',
        'Distribute updates to relevant agents',
        'Manage knowledge flow',
        'Balance workloads'
      ],
      schedule: '*/5 * * * *' // Every 5 minutes
    }));

    this.registerAgent('relationshipMapper', new RelationshipMapperAgent({
      name: 'Relationship Mapper',
      priority: 6,
      responsibilities: [
        'Map knowledge relationships',
        'Build connection graphs',
        'Identify dependencies',
        'Maintain knowledge links'
      ],
      schedule: '*/20 * * * *' // Every 20 minutes
    }));

    // OPTIMIZATION AGENTS
    this.registerAgent('memoryConsolidation', new MemoryConsolidationAgent({
      name: 'Memory Consolidation',
      priority: 6,
      responsibilities: [
        'Merge duplicate knowledge',
        'Compress old memories',
        'Strengthen important patterns',
        'Optimize storage'
      ],
      schedule: '0 3 * * *' // Daily at 3 AM
    }));

    this.registerAgent('cacheOptimizer', new CacheOptimizerAgent({
      name: 'Cache Optimizer',
      priority: 7,
      responsibilities: [
        'Manage cache layers',
        'Preload frequent queries',
        'Evict stale cache',
        'Optimize retrieval speed'
      ],
      schedule: '*/15 * * * *' // Every 15 minutes
    }));

    this.registerAgent('evolutionOptimizer', new EvolutionOptimizerAgent({
      name: 'Evolution Optimizer',
      priority: 5,
      responsibilities: [
        'Optimize knowledge structure',
        'Improve retrieval algorithms',
        'Enhance learning rates',
        'Evolve brain architecture'
      ],
      schedule: '0 4 * * *' // Daily at 4 AM
    }));

    // SEMANTIC & INTELLIGENCE AGENTS
    this.registerAgent('semanticAnalyzer', new SemanticAnalyzerAgent({
      name: 'Semantic Analyzer',
      priority: 6,
      responsibilities: [
        'Generate embeddings',
        'Semantic search optimization',
        'Context understanding',
        'Meaning extraction'
      ],
      schedule: '*/30 * * * *' // Every 30 minutes
    }));

    this.registerAgent('marketIntelligence', new MarketIntelligenceAgent({
      name: 'Market Intelligence',
      priority: 8,
      responsibilities: [
        'Monitor market conditions',
        'Update trading knowledge',
        'Track indicator performance',
        'Validate strategies'
      ],
      schedule: '*/5 * * * *' // Every 5 minutes during market hours
    }));

    // MAINTENANCE AGENTS
    this.registerAgent('conflictResolver', new ConflictResolverAgent({
      name: 'Conflict Resolver',
      priority: 9,
      responsibilities: [
        'Resolve knowledge conflicts',
        'Handle contradictions',
        'Merge conflicting patterns',
        'Maintain consistency'
      ],
      schedule: '*/10 * * * *' // Every 10 minutes
    }));

    this.registerAgent('archiveManager', new ArchiveManagerAgent({
      name: 'Archive Manager',
      priority: 5,
      responsibilities: [
        'Archive old knowledge',
        'Manage storage quotas',
        'Compress historical data',
        'Restore archived items'
      ],
      schedule: '0 2 * * *' // Daily at 2 AM
    }));

    console.log(`✅ Initialized ${this.agents.size} Brain Sub-Agents`);

    // Setup inter-agent communication
    this.setupAgentCommunication();

    // Start orchestration
    await this.startOrchestration();
  }

  /**
   * Register an agent in the orchestrator
   */
  registerAgent(id, agent) {
    this.agents.set(id, agent);

    // Setup agent event listeners
    agent.on('taskComplete', (result) => this.handleTaskComplete(id, result));
    agent.on('taskFailed', (error) => this.handleTaskFailed(id, error));
    agent.on('discovery', (data) => this.handleDiscovery(id, data));
    agent.on('alert', (alert) => this.handleAlert(id, alert));

    // Connect to message bus
    agent.setMessageBus(this.messageBus);
  }

  /**
   * Setup inter-agent communication channels
   */
  setupAgentCommunication() {
    // Knowledge flow: Validator -> Distributor -> Category Agents
    this.messageBus.on('knowledge:validated', async (data) => {
      await this.agents.get('dataDistributor').distribute(data);
    });

    // Pattern flow: Discovery -> Validator -> Knowledge Base
    this.messageBus.on('pattern:discovered', async (pattern) => {
      await this.agents.get('validator').validatePattern(pattern);
    });

    // Conflict flow: QC -> Resolver -> Validator
    this.messageBus.on('conflict:detected', async (conflict) => {
      await this.agents.get('conflictResolver').resolve(conflict);
    });

    // Cache flow: Frequently accessed -> Cache Optimizer
    this.messageBus.on('knowledge:accessed', async (id) => {
      await this.agents.get('cacheOptimizer').trackAccess(id);
    });

    // Learning flow: User interaction -> Learning Pipeline
    this.messageBus.on('user:interaction', async (interaction) => {
      await this.agents.get('learningPipeline').process(interaction);
    });

    // Archive flow: Old data -> Archive Manager
    this.messageBus.on('knowledge:stale', async (items) => {
      await this.agents.get('archiveManager').archive(items);
    });
  }

  /**
   * Start the orchestration system
   */
  async startOrchestration() {
    if (this.state.isRunning) {
      console.log('⚠️ Orchestration already running');
      return;
    }

    this.state.isRunning = true;
    console.log('🚀 Starting Brain Sub-Agents Orchestration');

    // Start all agents
    for (const [id, agent] of this.agents) {
      await this.startAgent(id);
    }

    // Start task scheduler
    this.startTaskScheduler();

    // Start health monitoring
    this.startHealthMonitoring();

    // Start coordination loop
    this.startCoordinationLoop();

    console.log('✅ Brain Orchestration System Active');
  }

  /**
   * Start individual agent
   */
  async startAgent(agentId) {
    try {
      const agent = this.agents.get(agentId);
      if (!agent) return;

      await agent.start();
      this.state.activeAgents.add(agentId);
      console.log(`✅ Started agent: ${agent.config.name}`);

    } catch (error) {
      console.error(`❌ Failed to start agent ${agentId}:`, error);
    }
  }

  /**
   * Task scheduling system
   */
  startTaskScheduler() {
    // Check for pending tasks every second
    setInterval(() => {
      this.processPendingTasks();
    }, 1000);

    // Schedule agent-specific tasks based on their schedules
    for (const [id, agent] of this.agents) {
      if (agent.config.schedule) {
        this.scheduleAgentTask(id, agent.config.schedule);
      }
    }
  }

  /**
   * Process pending tasks in queue
   */
  async processPendingTasks() {
    if (this.state.queuedTasks.length === 0) return;

    // Sort by priority
    this.state.queuedTasks.sort((a, b) => b.priority - a.priority);

    // Process tasks up to concurrency limit
    const concurrencyLimit = 5;
    const tasksToProcess = this.state.queuedTasks.splice(0, concurrencyLimit);

    for (const task of tasksToProcess) {
      this.executeTask(task);
    }
  }

  /**
   * Execute a specific task
   */
  async executeTask(task) {
    const startTime = Date.now();

    try {
      const agent = this.agents.get(task.agentId);
      if (!agent) throw new Error(`Agent ${task.agentId} not found`);

      const result = await agent.execute(task);

      this.handleTaskComplete(task.agentId, {
        taskId: task.id,
        result,
        duration: Date.now() - startTime
      });

    } catch (error) {
      this.handleTaskFailed(task.agentId, {
        taskId: task.id,
        error,
        duration: Date.now() - startTime
      });
    }
  }

  /**
   * Health monitoring system
   */
  startHealthMonitoring() {
    setInterval(async () => {
      const health = await this.checkSystemHealth();

      if (health.status !== 'healthy') {
        console.warn('⚠️ Brain health issue detected:', health);
        await this.performHealthRecovery(health);
      }

      // Store health metrics
      await this.storeHealthMetrics(health);

    }, 60000); // Every minute
  }

  /**
   * Check overall system health
   */
  async checkSystemHealth() {
    const health = {
      timestamp: Date.now(),
      status: 'healthy',
      agents: {},
      metrics: {},
      issues: []
    };

    // Check each agent
    for (const [id, agent] of this.agents) {
      const agentHealth = await agent.getHealth();
      health.agents[id] = agentHealth;

      if (agentHealth.status !== 'healthy') {
        health.issues.push({
          agent: id,
          issue: agentHealth.issue
        });
      }
    }

    // Check database health
    try {
      const { count } = await this.supabase
        .from('brain_knowledge')
        .select('*', { count: 'exact', head: true });

      health.metrics.totalKnowledge = count;
    } catch (error) {
      health.issues.push({
        component: 'database',
        issue: error.message
      });
    }

    // Check memory usage
    const memUsage = process.memoryUsage();
    health.metrics.memoryUsage = Math.round(memUsage.heapUsed / 1024 / 1024);

    if (health.metrics.memoryUsage > 500) { // 500MB threshold
      health.issues.push({
        component: 'memory',
        issue: 'High memory usage'
      });
    }

    // Determine overall status
    if (health.issues.length > 3) {
      health.status = 'critical';
    } else if (health.issues.length > 0) {
      health.status = 'degraded';
    }

    return health;
  }

  /**
   * Coordination loop for agent synchronization
   */
  startCoordinationLoop() {
    setInterval(async () => {
      await this.coordinateAgents();
    }, 5000); // Every 5 seconds
  }

  /**
   * Coordinate agent activities
   */
  async coordinateAgents() {
    // Check for agent dependencies
    for (const [id, agent] of this.agents) {
      if (agent.hasPendingDependencies()) {
        await this.resolveDependencies(id);
      }
    }

    // Balance workloads
    await this.balanceWorkloads();

    // Sync agent states
    await this.syncAgentStates();
  }

  /**
   * Balance workloads across agents
   */
  async balanceWorkloads() {
    const workloads = new Map();

    // Get current workloads
    for (const [id, agent] of this.agents) {
      workloads.set(id, await agent.getWorkload());
    }

    // Find overloaded agents
    const overloaded = Array.from(workloads.entries())
      .filter(([id, load]) => load > 80);

    // Redistribute if necessary
    for (const [overloadedId, load] of overloaded) {
      const agent = this.agents.get(overloadedId);
      const tasks = await agent.getRedistributableTasks();

      // Find agents with capacity
      const available = Array.from(workloads.entries())
        .filter(([id, load]) => load < 50)
        .sort((a, b) => a[1] - b[1]);

      if (available.length > 0) {
        const [targetId] = available[0];
        await this.redistributeTasks(tasks, overloadedId, targetId);
      }
    }
  }

  /**
   * Handle task completion
   */
  handleTaskComplete(agentId, result) {
    this.state.completedTasks.push({
      agentId,
      timestamp: Date.now(),
      ...result
    });

    this.state.metrics.completedTasks++;
    this.updateAverageProcessingTime(result.duration);

    // Emit completion event
    this.emit('taskComplete', { agentId, result });

    // Trigger dependent tasks
    this.triggerDependentTasks(agentId, result);
  }

  /**
   * Handle task failure
   */
  handleTaskFailed(agentId, error) {
    console.error(`❌ Task failed in ${agentId}:`, error);

    this.state.metrics.failedTasks++;

    // Attempt retry for critical agents
    const agent = this.agents.get(agentId);
    if (agent.config.priority >= 8 && error.retryCount < 3) {
      this.queueTask({
        ...error,
        retryCount: (error.retryCount || 0) + 1,
        agentId
      });
    }

    // Emit failure event
    this.emit('taskFailed', { agentId, error });
  }

  /**
   * Handle discoveries from agents
   */
  handleDiscovery(agentId, discovery) {
    console.log(`🔍 Discovery from ${agentId}:`, discovery);

    // Route discovery to appropriate agents
    this.messageBus.emit('discovery:new', {
      source: agentId,
      discovery,
      timestamp: Date.now()
    });

    // Store discovery
    this.storeDiscovery(agentId, discovery);
  }

  /**
   * Handle alerts from agents
   */
  handleAlert(agentId, alert) {
    console.log(`🚨 Alert from ${agentId}:`, alert);

    // Route alert based on severity
    if (alert.severity === 'critical') {
      this.handleCriticalAlert(agentId, alert);
    } else {
      this.messageBus.emit('alert:new', {
        source: agentId,
        alert,
        timestamp: Date.now()
      });
    }
  }

  /**
   * Store discovery in database
   */
  async storeDiscovery(agentId, discovery) {
    await this.supabase.from('brain_discoveries').insert({
      agent_id: agentId,
      discovery_type: discovery.type,
      content: discovery.content,
      confidence: discovery.confidence,
      metadata: discovery.metadata
    });
  }

  /**
   * Get orchestrator status
   */
  getStatus() {
    return {
      isRunning: this.state.isRunning,
      activeAgents: Array.from(this.state.activeAgents),
      queuedTasks: this.state.queuedTasks.length,
      completedTasks: this.state.completedTasks.length,
      metrics: this.state.metrics,
      agentStatuses: Array.from(this.agents.entries()).map(([id, agent]) => ({
        id,
        name: agent.config.name,
        status: agent.getStatus()
      }))
    };
  }

  /**
   * Queue a task for processing
   */
  queueTask(task) {
    this.state.queuedTasks.push({
      id: crypto.randomUUID(),
      timestamp: Date.now(),
      priority: task.priority || 5,
      ...task
    });
    this.state.metrics.totalTasks++;
  }

  /**
   * Update average processing time
   */
  updateAverageProcessingTime(duration) {
    const alpha = 0.1; // Exponential moving average factor
    this.state.metrics.avgProcessingTime =
      alpha * duration + (1 - alpha) * this.state.metrics.avgProcessingTime;
  }

  /**
   * Graceful shutdown
   */
  async shutdown() {
    console.log('🛑 Shutting down Brain Orchestration System');

    this.state.isRunning = false;

    // Stop all agents
    for (const [id, agent] of this.agents) {
      await agent.stop();
    }

    // Clear queues
    this.state.queuedTasks = [];

    console.log('✅ Brain Orchestration System shut down');
  }
}

// Export singleton instance
const orchestrator = new BrainSubAgentsOrchestrator();
export default orchestrator;
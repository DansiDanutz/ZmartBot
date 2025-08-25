.PHONY: infra-up infra-down infra-logs diana-up diana-status

diana-up: infra-up diana-status
	@echo "🚀 DIANA Platform ready in 2 minutes!"

infra-up:
	docker compose -f infra/compose.yml up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 30

infra-down:
	docker compose -f infra/compose.yml down -v

infra-logs:
	docker compose -f infra/compose.yml logs -f --tail=200

diana-status:
	@echo "📊 DIANA Platform Status:"
	@echo "RabbitMQ UI:  http://localhost:15672 (guest/guest)"
	@echo "Jaeger UI:    http://localhost:16686"
	@echo "Prometheus:   http://localhost:9090"
	@echo "Grafana:      http://localhost:3000 (admin/admin)"
	@echo "PostgreSQL:   localhost:5432 (zmart/zmart/zmart_core)"
	@echo "Redis:        localhost:6379"

diana-test:
	@echo "🧪 Testing DIANA Platform Services..."
	@curl -s http://localhost:15672/api/overview | jq -r '.rabbitmq_version' && echo "✅ RabbitMQ Ready"
	@curl -s http://localhost:16686/api/services | jq length && echo "✅ Jaeger Ready" 
	@curl -s http://localhost:9090/api/v1/status/config | jq -r '.status' && echo "✅ Prometheus Ready"
	@curl -s http://localhost:3000/api/health && echo "✅ Grafana Ready"
	@curl -s http://localhost:8080/health && echo "✅ Config Server Ready"
	@curl -s http://localhost:8500/v1/status/leader && echo "✅ Consul Ready"
	@curl -s http://localhost/health && echo "✅ API Gateway Ready"
	@echo "🎉 DIANA Platform is FULLY OPERATIONAL!"

diana-status-full:
	@echo "📊 DIANA Platform Complete Status Report:"
	@echo "🗄️  Infrastructure Services:"
	@echo "   PostgreSQL:   http://localhost:5432 (zmart/zmart/zmart_core)"
	@echo "   Redis:        http://localhost:6379"
	@echo "   RabbitMQ UI:  http://localhost:15672 (zmart_user/zmart_rabbitmq_password)"
	@echo ""
	@echo "🔍 Observability Stack:"
	@echo "   Jaeger UI:    http://localhost:16686"
	@echo "   Prometheus:   http://localhost:9090"
	@echo "   Grafana:      http://localhost:3000 (admin/admin)"
	@echo "   OpenTelemetry Collector: http://localhost:13133"
	@echo ""
	@echo "⚙️  Platform Services:"
	@echo "   Config Server: http://localhost:8080"
	@echo "   Consul UI:     http://localhost:8500"
	@echo "   API Gateway:   http://localhost"
	@echo ""
	@echo "🚀 ZmartBot Integration:"
	@echo "   Main API:      http://localhost:8000"
	@echo "   Dashboard:     http://localhost:3400"
	@echo ""
	@echo "💡 Next Steps:"
	@echo "   1. Run: make diana-test"
	@echo "   2. Deploy ZmartBot services"  
	@echo "   3. Monitor via Grafana dashboards"

diana-logs:
	docker compose -f infra/compose.yml logs -f --tail=100

diana-clean:
	docker compose -f infra/compose.yml down -v --remove-orphans
	docker system prune -f

diana-restart: diana-down diana-up
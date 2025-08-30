// Configuração Railway para agentes MCP
module.exports = {
    project: {
        id: '41555273-319a-4fd5-af0e-b743861c29fa',
        name: 'sistema-meep',
        region: 'us-west1'
    },
    
    services: {
        frontend: {
            name: 'sistema-meep-frontend',
            type: 'web',
            buildCommand: 'cd paineluniversal/frontend && npm install && npm run build',
            startCommand: 'cd paineluniversal/frontend && npx serve -s dist -l $PORT',
            healthcheckPath: '/',
            rootDirectory: 'paineluniversal/frontend',
            watchPaths: ['paineluniversal/frontend/**']
        },
        
        backend: {
            name: 'sistema-meep-backend',
            type: 'web',
            buildCommand: 'cd paineluniversal/backend && pip install -r requirements.txt',
            startCommand: 'cd paineluniversal/backend && uvicorn main:app --host 0.0.0.0 --port $PORT',
            healthcheckPath: '/api/health',
            rootDirectory: 'paineluniversal/backend',
            watchPaths: ['paineluniversal/backend/**']
        }
    },
    
    environment: {
        production: {
            NODE_ENV: 'production',
            PYTHONUNBUFFERED: '1',
            PORT: '3000',
            API_PORT: '8000'
        }
    },
    
    deploy: {
        autoDeploy: true,
        branch: 'main',
        prDeploy: true,
        restartPolicy: 'ON_FAILURE',
        maxRestarts: 10
    },
    
    monitoring: {
        enabled: true,
        alertThreshold: {
            errorRate: 0.05,
            responseTime: 1000,
            uptime: 0.99
        }
    },
    
    scaling: {
        minInstances: 1,
        maxInstances: 3,
        targetCPU: 70,
        targetMemory: 80
    }
};
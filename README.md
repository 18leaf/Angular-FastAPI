IN Angular
change angular.json find architecture.serve ADD options =

        "serve": {
          "builder": "@angular-devkit/build-angular:dev-server",
          "configurations": {
            "production": {
              "browserTarget": "test-frontend:build:production"
            },
            "development": {
              "browserTarget": "test-frontend:build:development"
            }
          },
           "options": {
              "browserTarget": "test-frontend:build",
              "proxyConfig": "src/proxy.conf.json"
            },
          "defaultConfiguration": "development"
        },

create proxy.conf.json in src directory add following to allow CORS:

        {
            "/api/*": {
                "target": "http://localhost:8000",
                "secure": false,
                "logLevel": "debug"
            }
        }

ENABLE cors in Fast API app:

    app = FastAPI()
    app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers)

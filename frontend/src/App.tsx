import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <header className="mb-8">
            <h1 className="text-4xl font-bold text-primary">
              AI Code Review Assistant
            </h1>
            <p className="text-muted-foreground mt-2">
              Sprint 0: Project Setup Complete
            </p>
          </header>
          <main>
            <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
              <h2 className="text-2xl font-semibold mb-4">Welcome!</h2>
              <p className="text-muted-foreground">
                The frontend development environment is set up and ready.
              </p>
              <div className="mt-6 space-y-2">
                <p className="font-medium">Next Steps:</p>
                <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                  <li>Sprint 1: Backend Foundation (Database Models & APIs)</li>
                  <li>Sprint 2: GitHub Integration</li>
                  <li>Sprint 3-4: Analysis Pipeline</li>
                  <li>Sprint 5-7: Frontend Features</li>
                </ul>
              </div>
            </div>
          </main>
        </div>
      </div>
    </QueryClientProvider>
  )
}

export default App

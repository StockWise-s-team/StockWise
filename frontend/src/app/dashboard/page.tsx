export default function DashboardPage() {
  return (
    <div>
      <h1 className="mb-4 text-3xl font-bold">Dashboard</h1>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-lg border bg-card p-4 shadow-sm">
          <h2 className="text-sm font-medium text-muted-foreground">
            Portfolio Value
          </h2>
          <p className="mt-2 text-2xl font-bold">$0.00</p>
        </div>
        <div className="rounded-lg border bg-card p-4 shadow-sm">
          <h2 className="text-sm font-medium text-muted-foreground">
            Virtual Cash
          </h2>
          <p className="mt-2 text-2xl font-bold">$100,000.00</p>
        </div>
        <div className="rounded-lg border bg-card p-4 shadow-sm">
          <h2 className="text-sm font-medium text-muted-foreground">
            Total P/L
          </h2>
          <p className="mt-2 text-2xl font-bold text-green-600">+$0.00</p>
        </div>
      </div>
    </div>
  );
}

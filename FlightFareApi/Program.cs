// ********************************************************************
//  FlightFareApi – Minimal API bootstrap
// ********************************************************************
using System.Data;
using Dapper;
using DuckDB.NET.Data;
using Microsoft.AspNetCore.SignalR;
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

// -------------------------------------------------
// 1) Logging – console w/ scopes & UTC timestamps
// -------------------------------------------------
builder.Logging.ClearProviders()
               .AddSimpleConsole(o =>
               {
                   o.IncludeScopes = true;
                   o.SingleLine = true;
                   o.TimestampFormat = "yyyy-MM-ddTHH:mm:ssZ ";
               });

// -------------------------------------------------
// 2) Services / DI
// -------------------------------------------------
builder.Services.AddSingleton<IDbConnection>(sp =>
{
    // Ensure the file lives under data/duckdb; DuckDB will create it if missing
    var conn = new DuckDBConnection("DataSource=data/duckdb/flights.duckdb");
    conn.Open();
    return conn;
});

builder.Services.AddSignalR();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(cfg =>
{
    cfg.SwaggerDoc("v1", new OpenApiInfo
    {
        Title       = "Flight-Fare API",
        Version     = "v1",
        Description = "DuckDB + Dapper + SignalR minimal API"
    });
});

var app = builder.Build();

// -------------------------------------------------
// 3) Global exception / not-found handling
// -------------------------------------------------
app.Use(async (ctx, next) =>
{
    try
    {
        await next();
        if (ctx.Response.StatusCode == 404)
        {
            await ctx.Response.WriteAsJsonAsync(new { error = "Route not found" });
        }
    }
    catch (Exception ex)
    {
        app.Logger.LogError(ex, "Unhandled exception");
        ctx.Response.StatusCode = 500;
        await ctx.Response.WriteAsJsonAsync(new { error = ex.Message });
    }
});

app.UseSwagger();
app.UseSwaggerUI();

// -------------------------------------------------
// 4) SignalR hub
// -------------------------------------------------
app.MapHub<LiveFeedHub>("/hub/live");

// -------------------------------------------------
// 5) REST endpoints
// -------------------------------------------------

// Health-check
app.MapGet("/health", () => Results.Ok(new { status = "ok", ts = DateTime.UtcNow }))
   .WithName("HealthCheck")
   .WithTags("Utility");

// Price history – simple sample query
app.MapGet("/prices/history", async (IDbConnection conn) =>
{
    const string sql = """
        SELECT days_left, ROUND(AVG(price),0) AS avg_price
        FROM flights_gold
        GROUP BY days_left
        ORDER BY days_left;
        """;
    var rows = await conn.QueryAsync(sql);
    return Results.Ok(rows);
})
.WithName("PriceHistory")
.WithTags("Prices");

// Endpoint to broadcast a manual message (demo only)
app.MapPost("/broadcast", async (BroadcastRequest req, IHubContext<LiveFeedHub> hub) =>
{
    await hub.Clients.All.SendAsync("priceUpdate", req);
    return Results.Accepted();
});

// -------------------------------------------------
// 6) Run
// -------------------------------------------------
app.Logger.LogInformation("🌐 Flight-Fare API running at {Url}", app.Urls.First());
app.Run();

// ********************************************************************
//  Supporting types
// ********************************************************************
record BroadcastRequest(string Airline, string Flight, string Source, string Destination, decimal Price);

class LiveFeedHub : Hub { }

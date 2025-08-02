using System.Data;
using System.Collections.Generic;
using System.Linq;
using Dapper;
using Microsoft.Extensions.Logging;

namespace FlightFareApi.Repositories;

public class FlightRepository
{
    private readonly IDbConnection _db;
    private readonly ILogger<FlightRepository> _logger;

    public FlightRepository(IDbConnection db, ILogger<FlightRepository> logger)
    {
        _db = db;
        _logger = logger;
    }

    public async Task<IEnumerable<dynamic>> GetLatestFlightsAsync()
    {
        const string sql = "SELECT * FROM flights_gold ORDER BY load_ts DESC LIMIT 100";
        try
        {
            return await _db.QueryAsync(sql);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Latest flights unavailable - returning empty set");
            return Enumerable.Empty<dynamic>();
        }
    }
}

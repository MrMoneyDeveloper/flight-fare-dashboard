using System.Data;
using Dapper;

namespace FlightFareApi.Repositories;

public class FlightRepository
{
    private readonly IDbConnection _db;
    public FlightRepository(IDbConnection db)
    {
        _db = db;
    }

    public async Task<IEnumerable<dynamic>> GetLatestFlightsAsync()
    {
        const string sql = "SELECT * FROM flights_gold ORDER BY load_ts DESC LIMIT 100";
        return await _db.QueryAsync(sql);
    }
}

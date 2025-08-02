namespace FlightFareApi.Models;

// Represents a single flight record returned by the API
public record Flight(
    string Airline,
    string FlightNumber,
    string Source,
    string Destination,
    decimal Price,
    int DaysLeft
);

namespace FlightFareApi.Models;

public record Flight(string Airline, string Flight, string Source, string Destination, decimal Price, int DaysLeft);

using System;
using System.Net.Http;
using System.Threading.Tasks;

namespace MirohaMonolith.Hardware
{
    class LegionBridge
    {
        private static readonly HttpClient client = new HttpClient();

        static async Task Main(string[] args)
        {
            Console.WriteLine("🛰️ [C# HARDWARE BRIDGE]: Контур контроллеров БСУ запущен...");
            
            // Моделируем перехват крохи данных с лазерного весового датчика
            string clientId = "CID-2026-99";
            double capturedWeightTons = 45.85;

            try 
            {
                var values = new System.Collections.Generic.Dictionary<string, string>
                {
                    { "client_id", clientId },
                    { "vor_value", capturedWeightTons.ToString() }
                };

                var content = new FormUrlEncodedContent(values);
                // C# выстреливает логом напрямую в наш FastAPI Docker-контейнер
                var response = await client.PostAsync("http://192.168.0", content);
                string responseString = await response.Content.ReadAsStringStringAsync();
                
                Console.WriteLine($"✅ [C# ВЫСТРЕЛ В PostgreSQL УСПЕШЕН]: {responseString}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ [C# КЛИНЧ СЕТИ]: {ex.Message}");
            }
        }
    }
}

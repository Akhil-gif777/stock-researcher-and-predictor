import type {
  StockAnalysisResult,
  ChartDataResponse,
  AgentUpdate,
  InvestmentStyle,
} from "../types/api";

const API_BASE_URL = "http://localhost:8000";
const WS_BASE_URL = "ws://localhost:8000";

export class StockAnalysisAPI {
  private ws: WebSocket | null = null;

  /**
   * Connect to WebSocket for real-time analysis updates
   */
  connectWebSocket(
    symbol: string,
    style: InvestmentStyle,
    onUpdate: (update: AgentUpdate) => void,
    onComplete: (result: StockAnalysisResult) => void,
    onError: (error: Error) => void
  ): () => void {
    const wsUrl = `${WS_BASE_URL}/ws/analyze/${symbol.toUpperCase()}?style=${style}`;
    console.log("🔄 Connecting to WebSocket:", wsUrl);
    
    try {
      this.ws = new WebSocket(wsUrl);

      // Add connection timeout
      const connectionTimeout = setTimeout(() => {
        if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
          console.error("❌ WebSocket connection timeout");
          this.ws.close();
          onError(new Error("WebSocket connection timeout"));
        }
      }, 10000); // 10 second timeout

      this.ws.onopen = () => {
        console.log("✅ WebSocket connected successfully");
        console.log("🔄 WebSocket URL:", wsUrl);
        console.log("🔄 WebSocket readyState:", this.ws?.readyState);
        clearTimeout(connectionTimeout);
      };

      this.ws.onmessage = (event) => {
        try {
          const update: AgentUpdate = JSON.parse(event.data);
          console.log("🔄 WebSocket RAW message:", event.data);
          console.log("🔄 WebSocket PARSED update:", update);

          // If it's the final result with data
          if (update.status === "completed" && update.data) {
            console.log("✅ Analysis complete, calling onComplete with:", update.data);
            onComplete(update.data);
          } else {
            // Regular agent update - log the status mapping
            console.log(`📡 Agent update: ${update.agent} -> ${update.status} (${update.message})`);
            onUpdate(update);
          }
        } catch (err) {
          console.error("❌ Error parsing WebSocket message:", err, "Raw data:", event.data);
          onError(new Error("Failed to parse server message"));
        }
      };

      this.ws.onerror = (event) => {
        console.error("❌ WebSocket error:", event);
        console.error("❌ WebSocket URL:", wsUrl);
        console.error("❌ WebSocket readyState:", this.ws?.readyState);
        onError(new Error("WebSocket connection error"));
      };

      this.ws.onclose = (event) => {
        console.log("WebSocket closed:", event.code, event.reason);
        if (!event.wasClean) {
          onError(new Error("WebSocket connection lost"));
        }
      };

      // Return cleanup function
      return () => {
        clearTimeout(connectionTimeout);
        if (this.ws) {
          this.ws.close();
          this.ws = null;
        }
      };
    } catch (err) {
      onError(err as Error);
      return () => {};
    }
  }

  /**
   * Fetch chart data for a stock
   */
  async getChartData(
    symbol: string,
    period: string = "90d"
  ): Promise<ChartDataResponse> {
    const url = `${API_BASE_URL}/api/stock/${symbol.toUpperCase()}/chart-data?period=${period}`;
    console.log("🔄 Fetching chart data from:", url);
    
    try {
      const response = await fetch(url);
      console.log("🔄 Chart data response status:", response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("❌ Chart data error response:", errorText);
        
        // Handle specific backend errors
        if (response.status === 500 && errorText.includes("MACD")) {
          console.warn("⚠️ Backend MACD calculation error - this is a known issue");
          throw new Error("Chart data temporarily unavailable due to indicator calculation error (MACD). This is a backend issue that needs to be fixed.");
        }
        
        throw new Error(`Failed to fetch chart data (${response.status}): ${response.statusText} - ${errorText}`);
      }

      const data = await response.json();
      console.log("✅ Chart data received:", data);
      console.log("🔄 Chart data structure:", {
        has_chart_data: !!data.chart_data,
        chart_data_type: typeof data.chart_data,
        chart_data_keys: data.chart_data ? Object.keys(data.chart_data) : null,
        timestamps_length: data.chart_data?.timestamps?.length,
        sma_20_length: data.chart_data?.sma_20?.length,
        sma_50_length: data.chart_data?.sma_50?.length,  
        ema_12_length: data.chart_data?.ema_12?.length,
      });
      
      if (!data.chart_data) {
        console.warn("⚠️ No chart_data field in response:", data);
        throw new Error("No chart data field in server response");
      }

      // Handle different chart data formats
      let transformedData = data;
      
      // If chart_data is an object with arrays (backend format), transform to array format
      if (typeof data.chart_data === 'object' && !Array.isArray(data.chart_data)) {
        console.log("🔄 Transforming object-based chart data to array format");
        
        const { timestamps, open, high, low, close, volume, sma_20, sma_50, sma_200, ema_12, ema_26 } = data.chart_data;
        
        if (!timestamps || !Array.isArray(timestamps) || timestamps.length === 0) {
          console.warn("⚠️ No valid timestamps in chart data");
          throw new Error("No valid timestamp data available");
        }
        
        // Transform to array of data points
        const chartDataArray = timestamps.map((timestamp: string, index: number) => ({
          date: timestamp,
          price: close?.[index] || 0,
          open: open?.[index] || 0,
          high: high?.[index] || 0,
          low: low?.[index] || 0,
          close: close?.[index] || 0,
          volume: volume?.[index] || 0,
          sma20: sma_20?.[index] || null,
          sma50: sma_50?.[index] || null,
          sma200: sma_200?.[index] || null,
          ema12: ema_12?.[index] || null,
          ema26: ema_26?.[index] || null,
        }));
        
        console.log("✅ Transformed chart data array:", {
          length: chartDataArray.length,
          first_point: chartDataArray[0],
          last_point: chartDataArray[chartDataArray.length - 1]
        });
        
        transformedData = {
          ...data,
          chart_data: chartDataArray
        };
      }
      // If chart_data is already an array, validate it
      else if (Array.isArray(data.chart_data)) {
        if (data.chart_data.length === 0) {
          console.warn("⚠️ Empty chart data array received");
          throw new Error("No chart data points available for this stock");
        }
        console.log("✅ Chart data already in array format, length:", data.chart_data.length);
      }
      else {
        console.warn("⚠️ Unexpected chart data format:", typeof data.chart_data);
        throw new Error("Unexpected chart data format received from server");
      }

      return transformedData;
    } catch (err) {
      console.error("❌ Error fetching chart data:", err);
      throw err;
    }
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<boolean> {
    try {
      console.log("🔄 Health check:", `${API_BASE_URL}/health`);
      const response = await fetch(`${API_BASE_URL}/health`);
      console.log("🔄 Health check response:", response.status, response.statusText);
      
      if (response.ok) {
        const data = await response.text();
        console.log("✅ Health check successful:", data);
        return true;
      } else {
        console.error("❌ Health check failed:", response.status, response.statusText);
        return false;
      }
    } catch (err) {
      console.error("❌ Health check network error:", err);
      return false;
    }
  }

  /**
   * Test chart data endpoint with a known stock symbol
   */
  async testChartDataEndpoint(): Promise<boolean> {
    try {
      console.log("🔄 Testing chart data endpoint with AAPL...");
      await this.getChartData("AAPL", "30d");
      console.log("✅ Chart data endpoint test successful");
      return true;
    } catch (err) {
      console.error("❌ Chart data endpoint test failed:", err);
      return false;
    }
  }

  /**
   * Close WebSocket connection
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Singleton instance
export const stockAnalysisAPI = new StockAnalysisAPI();


//+------------------------------------------------------------------+
//|                                    SimplifiedGoldmine_v1.mq5      |
//|                     Simplified from Goldmine Combined EA v4.0      |
//|                   RSI Signal + Reverse Trading + Daily Limits      |
//+------------------------------------------------------------------+
#property copyright "Simplified Goldmine v1.0"
#property version   "1.00"
#property strict

//+------------------------------------------------------------------+
//| Input Parameters                                                   |
//+------------------------------------------------------------------+
input group "=== RSI Signal Settings ==="
input int RSI_Period = 14;                              // RSI Period
input ENUM_TIMEFRAMES RSI_Timeframe = PERIOD_M5;        // RSI Timeframe
input double RSI_OversoldLevel = 35.0;                  // RSI Oversold Level (Buy Signal when crossing UP)
input double RSI_OverboughtLevel = 65.0;                // RSI Overbought Level (Sell Signal when crossing DOWN)

input group "=== Timeframe Settings ==="
input ENUM_TIMEFRAMES TF_Signal = PERIOD_M3;            // Signal Check Timeframe (bar frequency)
input ENUM_TIMEFRAMES TF_Trend1 = PERIOD_M1;            // Trend Analysis Timeframe 1
input ENUM_TIMEFRAMES TF_Trend2 = PERIOD_M5;            // Trend Analysis Timeframe 2
input ENUM_TIMEFRAMES TF_Trend3 = PERIOD_M3;            // Trend Analysis Timeframe 3

input group "=== Trade Settings ==="
input double LotSize = 0.01;                            // Lot Size (fixed)
input int Slippage = 30;                                // Slippage in Points
input int MagicNumber = 789012003;                      // Magic Number
input int MinBarsForSwing = 5;                          // Min Bars for Swing Detection (Trend Analysis)

input group "=== Trend Filter ==="
input bool UseTrendFilter = true;                       // Enable Trend Alignment Filter
input bool AllowCounterTrend = false;                   // Allow Counter-Trend Trades

input group "=== 1H EMA Trend Gate ==="
input bool UseEMATrendGate = true;                      // Enable EMA Trend Gate Filter
input int EMATrendGatePeriod = 50;                      // EMA Period for Trend Gate
input ENUM_TIMEFRAMES EMATrendGateTF = PERIOD_H1;       // Timeframe for EMA Trend Gate

input group "=== Volume Profile / POC Filter ==="
input bool UsePOCFilter = true;                         // Enable Volume Profile POC Filter
input int POC_LookbackBars = 24;                        // H1 Bars Lookback for POC
input ENUM_TIMEFRAMES POC_ReclaimTF = PERIOD_M3;        // Timeframe for Candle Close Reclaim
input int POC_UpdateFrequency = 5;                      // POC Update Frequency (Minutes)

input group "=== Daily Limits ==="
input bool UseDailyLimits = true;                       // Enable Daily Profit/Loss Limits
input double DailyProfitTarget = 10.0;                  // Daily Profit Target ($)
input double DailyLossLimit = 400.0;                    // Daily Loss Limit ($)
input bool ResetDailyAtMidnight = true;                 // Reset Daily P/L at Midnight

input group "=== Order Filling ==="
input bool AutoDetectFilling = true;                    // Auto-detect best filling method

//+------------------------------------------------------------------+
//| Global Variables                                                   |
//+------------------------------------------------------------------+
// Indicator handles
int rsiSignalHandle = INVALID_HANDLE;
int emaTrendGateHandle = INVALID_HANDLE;

// RSI buffer
double rsiSignalBuffer[];

// Signal state
datetime lastBarTime = 0;
datetime lastSignalTime = 0;
int signalCount = 0;
int tradeCount = 0;

// POC Filter state
double lastPOCPrice = 0;
string currentPOCBias = "NEUTRAL";
datetime lastPOCUpdate = 0;
datetime lastPOCReclaimBarTime = 0;

// Reverse trade tracking
struct ReverseGroup {
    ulong ticket1;
    ulong ticket2;
    ulong ticket3;
    string type;       // "BUY" or "SELL"
    datetime openTime;
};

ReverseGroup reverseGroup;
bool syncActive = false;

// Daily limits tracking
double dailyProfitLoss = 0;
double dailyStartBalance = 0;
datetime currentTradingDay = 0;
bool dailyLimitReached = false;
string dailyLimitReason = "";

// Order filling mode
ENUM_ORDER_TYPE_FILLING currentFillingMode = ORDER_FILLING_FOK;

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
int OnInit()
{
    // Initialize RSI indicator for signal generation
    rsiSignalHandle = iRSI(_Symbol, RSI_Timeframe, RSI_Period, PRICE_CLOSE);
    if(rsiSignalHandle == INVALID_HANDLE)
    {
        Print("ERROR: Failed to create RSI signal indicator!");
        return(INIT_FAILED);
    }
    ArraySetAsSeries(rsiSignalBuffer, true);
    
    // Initialize EMA Trend Gate indicator
    if(UseEMATrendGate)
    {
        emaTrendGateHandle = iMA(_Symbol, EMATrendGateTF, EMATrendGatePeriod, 0, MODE_EMA, PRICE_CLOSE);
        if(emaTrendGateHandle == INVALID_HANDLE)
        {
            Print("ERROR: Failed to create EMA Trend Gate indicator!");
            return(INIT_FAILED);
        }
    }
    
    // Initialize state
    lastBarTime = 0;
    lastSignalTime = 0;
    ResetReverseGroup();
    
    // Detect and set filling mode
    currentFillingMode = DetectFillingMode();
    Print("Order Filling Mode: ", GetFillingModeDescription(currentFillingMode));
    
    // Initialize daily tracking
    InitializeDailyTracking();
    
    // Initialize POC Filter
    if(UsePOCFilter)
    {
        lastPOCPrice = CalculatePOC(PERIOD_H1, POC_LookbackBars);
        if(lastPOCPrice > 0)
        {
            double closePrev = iClose(_Symbol, POC_ReclaimTF, 1);
            if(closePrev > lastPOCPrice) currentPOCBias = "BULLISH";
            else if(closePrev < lastPOCPrice) currentPOCBias = "BEARISH";
            
            lastPOCUpdate = TimeCurrent();
            lastPOCReclaimBarTime = iTime(_Symbol, POC_ReclaimTF, 0);
            Print("Initial POC: ", DoubleToString(lastPOCPrice, _Digits), " | Bias: ", currentPOCBias);
        }
    }
    
    Print("==========================================");
    Print("Simplified Goldmine EA v1.0 Started");
    Print("Symbol: ", _Symbol);
    Print("Signal: RSI(", RSI_Period, ") on ", EnumToString(RSI_Timeframe));
    Print("  Oversold (Buy): ", DoubleToString(RSI_OversoldLevel, 1));
    Print("  Overbought (Sell): ", DoubleToString(RSI_OverboughtLevel, 1));
    Print("Signal Check TF: ", EnumToString(TF_Signal));
    Print("Trend TFs: ", EnumToString(TF_Trend1), " / ", EnumToString(TF_Trend2), " / ", EnumToString(TF_Trend3));
    Print("EMA Trend Gate: ", (UseEMATrendGate ? "ON (Period: " + IntegerToString(EMATrendGatePeriod) + " on " + EnumToString(EMATrendGateTF) + ")" : "OFF"));
    Print("POC Filter: ", (UsePOCFilter ? "ON" : "OFF"));
    Print("Daily Limits: ", (UseDailyLimits ? "ON (Profit: $" + DoubleToString(DailyProfitTarget, 2) + " / Loss: $" + DoubleToString(DailyLossLimit, 2) + ")" : "OFF"));
    Print("Lot Size: ", DoubleToString(LotSize, 2));
    Print("Magic Number: ", MagicNumber);
    Print("==========================================");
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    if(rsiSignalHandle != INVALID_HANDLE)
        IndicatorRelease(rsiSignalHandle);
    if(emaTrendGateHandle != INVALID_HANDLE)
        IndicatorRelease(emaTrendGateHandle);
    
    Print("Simplified Goldmine EA Stopped. Signals: ", signalCount, " | Trades: ", tradeCount);
}

//+------------------------------------------------------------------+
//| Expert tick function                                               |
//+------------------------------------------------------------------+
void OnTick()
{
    // Update POC Filter
    if(UsePOCFilter)
        UpdatePOCFilter();
    
    // Check and update daily limits
    if(UseDailyLimits)
    {
        CheckDailyReset();
        UpdateDailyPL();
        
        if(dailyLimitReached)
            return;
    }
    
    // Check for new bar on signal timeframe
    datetime currentBarTime = iTime(_Symbol, TF_Signal, 0);
    if(currentBarTime == lastBarTime)
        return;  // No new bar yet
    lastBarTime = currentBarTime;
    
    // Only check for signals when NO positions are open
    bool hasPositions = (CountOpenPositions() > 0);
    
    if(!hasPositions)
    {
        // Analyze trends for filtering
        string trend1 = AnalyzeTrend(TF_Trend1);
        string trend2 = AnalyzeTrend(TF_Trend2);
        string trend3 = AnalyzeTrend(TF_Trend3);
        
        // Check for RSI signal
        string signalType = "";
        if(CheckRSISignal(signalType))
        {
            // Apply trend filter
            if(!IsTrendAllowed(signalType, trend2, trend3))
                return;
            
            // Determine reverse direction
            string reverseType = (signalType == "BUY") ? "SELL" : "BUY";
            
            // Apply EMA Trend Gate (checks the REVERSE direction)
            if(UseEMATrendGate && !IsEMATrendGateAllowed(reverseType))
            {
                Print("=== REVERSE TRADE BLOCKED BY EMA GATE ===");
                return;
            }
            
            // Apply POC Filter (checks the REVERSE direction)
            if(UsePOCFilter && !IsPOCFilterAllowed(reverseType))
            {
                Print("=== REVERSE TRADE BLOCKED BY POC FILTER ===");
                return;
            }
            
            // All filters passed - execute reverse trades
            signalCount++;
            Print("=== NEW RSI SIGNAL #", signalCount, " ===");
            Print("RSI Signal: ", signalType, " → Reverse: ", reverseType);
            
            ExecuteReversePositions(reverseType);
        }
    }
}

//+------------------------------------------------------------------+
//| Check for RSI signal                                               |
//+------------------------------------------------------------------+
bool CheckRSISignal(string &signalType)
{
    // Prevent rapid signal generation
    if(TimeCurrent() - lastSignalTime < 60)
        return false;
    
    // Copy RSI data
    if(CopyBuffer(rsiSignalHandle, 0, 0, 3, rsiSignalBuffer) <= 0)
        return false;
    
    double currentRSI = rsiSignalBuffer[0];
    double prevRSI = rsiSignalBuffer[1];
    
    // Buy signal: RSI crosses UP through oversold level
    if(prevRSI < RSI_OversoldLevel && currentRSI >= RSI_OversoldLevel)
    {
        signalType = "BUY";
        lastSignalTime = TimeCurrent();
        Print("RSI BUY Signal: crossed above ", DoubleToString(RSI_OversoldLevel, 1),
              " (Prev: ", DoubleToString(prevRSI, 1), " → Curr: ", DoubleToString(currentRSI, 1), ")");
        return true;
    }
    
    // Sell signal: RSI crosses DOWN through overbought level
    if(prevRSI > RSI_OverboughtLevel && currentRSI <= RSI_OverboughtLevel)
    {
        signalType = "SELL";
        lastSignalTime = TimeCurrent();
        Print("RSI SELL Signal: crossed below ", DoubleToString(RSI_OverboughtLevel, 1),
              " (Prev: ", DoubleToString(prevRSI, 1), " → Curr: ", DoubleToString(currentRSI, 1), ")");
        return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Analyze trend using swing structure                                |
//+------------------------------------------------------------------+
string AnalyzeTrend(ENUM_TIMEFRAMES timeframe)
{
    double highs[], lows[], closes[];
    ArraySetAsSeries(highs, true);
    ArraySetAsSeries(lows, true);
    ArraySetAsSeries(closes, true);
    
    int bars = 50;
    if(CopyHigh(_Symbol, timeframe, 0, bars, highs) <= 0) return "NEUTRAL";
    if(CopyLow(_Symbol, timeframe, 0, bars, lows) <= 0) return "NEUTRAL";
    if(CopyClose(_Symbol, timeframe, 0, bars, closes) <= 0) return "NEUTRAL";
    
    // Count bullish/bearish bars in recent history
    int bullishBars = 0, bearishBars = 0;
    for(int i = 1; i < 10; i++)
    {
        if(closes[i] > closes[i+1]) bullishBars++;
        else bearishBars++;
    }
    
    // Detect swing highs and lows
    double swingHighs[], swingLows[];
    ArrayResize(swingHighs, 0);
    ArrayResize(swingLows, 0);
    
    for(int i = MinBarsForSwing; i < bars - MinBarsForSwing; i++)
    {
        bool isSwingHigh = true;
        bool isSwingLow = true;
        
        for(int j = 1; j <= MinBarsForSwing; j++)
        {
            if(highs[i] <= highs[i-j] || highs[i] <= highs[i+j]) isSwingHigh = false;
            if(lows[i] >= lows[i-j] || lows[i] >= lows[i+j]) isSwingLow = false;
        }
        
        if(isSwingHigh)
        {
            int size = ArraySize(swingHighs);
            ArrayResize(swingHighs, size + 1);
            swingHighs[size] = highs[i];
        }
        if(isSwingLow)
        {
            int size = ArraySize(swingLows);
            ArrayResize(swingLows, size + 1);
            swingLows[size] = lows[i];
        }
    }
    
    // Count higher highs and lower lows
    int hhCount = 0, llCount = 0;
    for(int i = 1; i < ArraySize(swingHighs); i++)
        if(swingHighs[i-1] > swingHighs[i]) hhCount++;
    for(int i = 1; i < ArraySize(swingLows); i++)
        if(swingLows[i-1] > swingLows[i]) llCount++;
    
    if((bullishBars > bearishBars && hhCount >= llCount) || bullishBars >= 7)
        return "BULLISH";
    else if((bearishBars > bullishBars && llCount >= hhCount) || bearishBars >= 7)
        return "BEARISH";
    return "NEUTRAL";
}

//+------------------------------------------------------------------+
//| Check if trend allows the signal                                   |
//+------------------------------------------------------------------+
bool IsTrendAllowed(string signalType, string trend2, string trend3)
{
    if(!UseTrendFilter || AllowCounterTrend)
        return true;
    
    // trend3 is the entry TF trend (TF_Trend3 = M3)
    // trend2 is the higher TF trend (TF_Trend2 = M5)
    if(signalType == "BUY")
    {
        return (trend3 == "BULLISH" || trend3 == "NEUTRAL" || 
                (trend2 == "BULLISH" && trend3 == "NEUTRAL"));
    }
    else if(signalType == "SELL")
    {
        return (trend3 == "BEARISH" || trend3 == "NEUTRAL" || 
                (trend2 == "BEARISH" && trend3 == "NEUTRAL"));
    }
    return true;
}

//+------------------------------------------------------------------+
//| EMA Trend Gate check                                               |
//+------------------------------------------------------------------+
bool IsEMATrendGateAllowed(string tradeType)
{
    if(!UseEMATrendGate || emaTrendGateHandle == INVALID_HANDLE)
        return true;
    
    double emaBuffer[];
    ArraySetAsSeries(emaBuffer, true);
    if(CopyBuffer(emaTrendGateHandle, 0, 0, 1, emaBuffer) <= 0)
        return true;  // Can't read EMA, allow trade
    
    double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
    double emaValue = emaBuffer[0];
    
    if(tradeType == "BUY")
        return (currentPrice > emaValue);
    else if(tradeType == "SELL")
        return (currentPrice < emaValue);
    
    return true;
}

//+------------------------------------------------------------------+
//| Calculate Volume Profile POC                                       |
//+------------------------------------------------------------------+
double CalculatePOC(ENUM_TIMEFRAMES tf, int lookback)
{
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    int copied = CopyRates(_Symbol, tf, 0, lookback, rates);
    if(copied <= 0) return 0;
    
    double highMax = -1;
    double lowMin = 1000000;
    for(int i = 0; i < copied; i++)
    {
        if(rates[i].high > highMax) highMax = rates[i].high;
        if(rates[i].low < lowMin) lowMin = rates[i].low;
    }
    
    if(highMax <= lowMin) return 0;
    
    const int binsCount = 150;
    double binWidth = (highMax - lowMin) / binsCount;
    double volumes[];
    ArrayResize(volumes, binsCount);
    ArrayInitialize(volumes, 0);
    
    for(int i = 0; i < copied; i++)
    {
        double barHigh = rates[i].high;
        double barLow = rates[i].low;
        long barVol = rates[i].tick_volume;
        
        int startBin = (int)((barLow - lowMin) / binWidth);
        int endBin = (int)((barHigh - lowMin) / binWidth);
        
        if(startBin < 0) startBin = 0;
        if(endBin >= binsCount) endBin = binsCount - 1;
        
        int span = endBin - startBin + 1;
        double volPerBin = (span > 0) ? (double)barVol / span : (double)barVol;
        
        for(int b = startBin; b <= endBin; b++)
            volumes[b] += volPerBin;
    }
    
    int maxBin = 0;
    double maxVol = -1;
    for(int b = 0; b < binsCount; b++)
    {
        if(volumes[b] > maxVol)
        {
            maxVol = volumes[b];
            maxBin = b;
        }
    }
    
    return NormalizeDouble(lowMin + (maxBin * binWidth) + (binWidth / 2.0), _Digits);
}

//+------------------------------------------------------------------+
//| Update POC Filter state                                            |
//+------------------------------------------------------------------+
void UpdatePOCFilter()
{
    datetime currentTime = TimeCurrent();
    
    // Recalculate POC periodically
    if(currentTime - lastPOCUpdate >= POC_UpdateFrequency * 60 || lastPOCPrice == 0)
    {
        double newPOC = CalculatePOC(PERIOD_H1, POC_LookbackBars);
        if(newPOC > 0)
        {
            lastPOCPrice = newPOC;
            lastPOCUpdate = currentTime;
        }
    }
    
    if(lastPOCPrice == 0) return;
    
    // Check for candle close reclaim
    datetime currentBarTime = iTime(_Symbol, POC_ReclaimTF, 0);
    if(currentBarTime != lastPOCReclaimBarTime)
    {
        double closePrev = iClose(_Symbol, POC_ReclaimTF, 1);
        string oldBias = currentPOCBias;
        
        if(closePrev > lastPOCPrice)
            currentPOCBias = "BULLISH";
        else if(closePrev < lastPOCPrice)
            currentPOCBias = "BEARISH";
        
        if(currentPOCBias != oldBias)
            Print("POC FILTER: Bias changed to ", currentPOCBias, " (POC: ", DoubleToString(lastPOCPrice, _Digits), ")");
        
        lastPOCReclaimBarTime = currentBarTime;
    }
}

//+------------------------------------------------------------------+
//| POC Filter check                                                   |
//+------------------------------------------------------------------+
bool IsPOCFilterAllowed(string tradeType)
{
    if(!UsePOCFilter) return true;
    
    if(tradeType == "BUY")
        return (currentPOCBias == "BULLISH");
    else if(tradeType == "SELL")
        return (currentPOCBias == "BEARISH");
    
    return true;
}

//+------------------------------------------------------------------+
//| Execute reverse positions (3 positions)                            |
//+------------------------------------------------------------------+
void ExecuteReversePositions(string reverseType)
{
    ResetReverseGroup();
    
    MqlTradeRequest request;
    MqlTradeResult result;
    ZeroMemory(request);
    ZeroMemory(result);
    
    request.action = TRADE_ACTION_DEAL;
    request.symbol = _Symbol;
    request.volume = LotSize;
    request.deviation = Slippage;
    request.magic = MagicNumber;
    request.sl = 0;
    request.tp = 0;
    request.type_filling = currentFillingMode;
    
    if(reverseType == "BUY")
    {
        request.type = ORDER_TYPE_BUY;
        request.price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
    }
    else
    {
        request.type = ORDER_TYPE_SELL;
        request.price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
    }
    
    // Open 3 positions
    request.comment = "Reverse1";
    if(OrderSend(request, result) && (result.retcode == TRADE_RETCODE_DONE || result.retcode == TRADE_RETCODE_PLACED))
        reverseGroup.ticket1 = result.order;
    else
        Print("ERROR: Failed to open Reverse1. Code: ", result.retcode, " - ", result.comment);
    
    Sleep(100);
    ZeroMemory(result);
    request.comment = "Reverse2";
    if(reverseType == "BUY")
        request.price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
    else
        request.price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
    if(OrderSend(request, result) && (result.retcode == TRADE_RETCODE_DONE || result.retcode == TRADE_RETCODE_PLACED))
        reverseGroup.ticket2 = result.order;
    else
        Print("ERROR: Failed to open Reverse2. Code: ", result.retcode, " - ", result.comment);
    
    Sleep(100);
    ZeroMemory(result);
    request.comment = "Reverse3";
    if(reverseType == "BUY")
        request.price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
    else
        request.price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
    if(OrderSend(request, result) && (result.retcode == TRADE_RETCODE_DONE || result.retcode == TRADE_RETCODE_PLACED))
        reverseGroup.ticket3 = result.order;
    else
        Print("ERROR: Failed to open Reverse3. Code: ", result.retcode, " - ", result.comment);
    
    // Verify all 3 opened successfully
    if(reverseGroup.ticket1 > 0 && reverseGroup.ticket2 > 0 && reverseGroup.ticket3 > 0)
    {
        reverseGroup.type = reverseType;
        reverseGroup.openTime = TimeCurrent();
        syncActive = true;
        tradeCount++;
        
        Print("=== REVERSE TRADE GROUP #", tradeCount, " OPENED ===");
        Print("Type: ", reverseType, " | Lots: 3 x ", DoubleToString(LotSize, 2));
        Print("Price: ", DoubleToString(request.price, _Digits));
    }
    else
    {
        // Close any partial fills
        Print("WARNING: Failed to open all 3 positions. Closing partial fills.");
        if(reverseGroup.ticket1 > 0) ClosePosition(reverseGroup.ticket1);
        if(reverseGroup.ticket2 > 0) ClosePosition(reverseGroup.ticket2);
        if(reverseGroup.ticket3 > 0) ClosePosition(reverseGroup.ticket3);
        ResetReverseGroup();
    }
}

//+------------------------------------------------------------------+
//| Count open positions with our magic number                         |
//+------------------------------------------------------------------+
int CountOpenPositions()
{
    int count = 0;
    for(int i = PositionsTotal() - 1; i >= 0; i--)
    {
        ulong ticket = PositionGetTicket(i);
        if(ticket > 0 && PositionGetString(POSITION_SYMBOL) == _Symbol && 
           PositionGetInteger(POSITION_MAGIC) == MagicNumber)
        {
            string comment = PositionGetString(POSITION_COMMENT);
            if(StringFind(comment, "Reverse") >= 0)
                count++;
        }
    }
    return count;
}

//+------------------------------------------------------------------+
//| Get current basket P/L (all reverse positions)                     |
//+------------------------------------------------------------------+
double GetCurrentBasketPL()
{
    double totalPL = 0;
    
    if(PositionSelectByTicket(reverseGroup.ticket1))
        totalPL += PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
    if(PositionSelectByTicket(reverseGroup.ticket2))
        totalPL += PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
    if(PositionSelectByTicket(reverseGroup.ticket3))
        totalPL += PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
    
    return totalPL;
}

//+------------------------------------------------------------------+
//| Close a position by ticket                                         |
//+------------------------------------------------------------------+
bool ClosePosition(ulong ticket)
{
    if(!PositionSelectByTicket(ticket)) return false;
    
    MqlTradeRequest request;
    MqlTradeResult result;
    ZeroMemory(request);
    ZeroMemory(result);
    
    request.action = TRADE_ACTION_DEAL;
    request.position = ticket;
    request.symbol = _Symbol;
    request.volume = PositionGetDouble(POSITION_VOLUME);
    request.deviation = Slippage;
    request.magic = MagicNumber;
    request.type_filling = currentFillingMode;
    
    ENUM_POSITION_TYPE posType = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
    if(posType == POSITION_TYPE_BUY)
    {
        request.type = ORDER_TYPE_SELL;
        request.price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
    }
    else
    {
        request.type = ORDER_TYPE_BUY;
        request.price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
    }
    
    return OrderSend(request, result) && (result.retcode == TRADE_RETCODE_DONE || result.retcode == TRADE_RETCODE_PLACED);
}

//+------------------------------------------------------------------+
//| Close all reverse positions                                        |
//+------------------------------------------------------------------+
void CloseAllPositions(string reason)
{
    Print("=== CLOSING ALL POSITIONS ===");
    Print("Reason: ", reason);
    
    if(reverseGroup.ticket1 > 0) ClosePosition(reverseGroup.ticket1);
    if(reverseGroup.ticket2 > 0) ClosePosition(reverseGroup.ticket2);
    if(reverseGroup.ticket3 > 0) ClosePosition(reverseGroup.ticket3);
    
    ResetReverseGroup();
}

//+------------------------------------------------------------------+
//| Reset reverse group state                                          |
//+------------------------------------------------------------------+
void ResetReverseGroup()
{
    reverseGroup.ticket1 = 0;
    reverseGroup.ticket2 = 0;
    reverseGroup.ticket3 = 0;
    reverseGroup.type = "";
    reverseGroup.openTime = 0;
    syncActive = false;
}

//+------------------------------------------------------------------+
//| Initialize daily tracking                                          |
//+------------------------------------------------------------------+
void InitializeDailyTracking()
{
    dailyStartBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    currentTradingDay = GetTradingDay();
    dailyProfitLoss = 0;
    dailyLimitReached = false;
    dailyLimitReason = "";
    
    Print("Daily tracking initialized. Balance: $", DoubleToString(dailyStartBalance, 2));
    Print("Daily Profit Target: $", DoubleToString(DailyProfitTarget, 2));
    Print("Daily Loss Limit: $", DoubleToString(DailyLossLimit, 2));
}

//+------------------------------------------------------------------+
//| Get trading day (midnight)                                         |
//+------------------------------------------------------------------+
datetime GetTradingDay()
{
    MqlDateTime dt;
    TimeToStruct(TimeCurrent(), dt);
    dt.hour = 0;
    dt.min = 0;
    dt.sec = 0;
    return StructToTime(dt);
}

//+------------------------------------------------------------------+
//| Check for daily reset                                              |
//+------------------------------------------------------------------+
void CheckDailyReset()
{
    if(!ResetDailyAtMidnight) return;
    
    datetime today = GetTradingDay();
    if(today != currentTradingDay)
    {
        currentTradingDay = today;
        dailyStartBalance = AccountInfoDouble(ACCOUNT_BALANCE);
        dailyProfitLoss = 0;
        dailyLimitReached = false;
        dailyLimitReason = "";
        
        Print("=== NEW DAY STARTED ===");
        Print("Balance: $", DoubleToString(dailyStartBalance, 2));
    }
}

//+------------------------------------------------------------------+
//| Update daily P/L and check limits                                  |
//+------------------------------------------------------------------+
void UpdateDailyPL()
{
    if(dailyLimitReached) return;
    
    // Calculate today's closed P/L
    double closedPL = CalculateTodaysClosedPL();
    
    // Add floating P/L from open reverse positions
    double floatingPL = GetCurrentBasketPL();
    
    // Total daily P/L
    dailyProfitLoss = closedPL + floatingPL;
    
    // Check daily profit target
    if(dailyProfitLoss >= DailyProfitTarget)
    {
        dailyLimitReached = true;
        dailyLimitReason = "Daily Profit Target Reached: $" + DoubleToString(dailyProfitLoss, 2);
        
        Print("=== DAILY PROFIT TARGET REACHED ===");
        Print("Target: $", DoubleToString(DailyProfitTarget, 2), " | Current: $", DoubleToString(dailyProfitLoss, 2));
        
        // Close all positions
        if(CountOpenPositions() > 0)
            CloseAllPositions("Daily profit target reached");
    }
    
    // Check daily loss limit
    if(dailyProfitLoss <= -DailyLossLimit)
    {
        dailyLimitReached = true;
        dailyLimitReason = "Daily Loss Limit Reached: $" + DoubleToString(dailyProfitLoss, 2);
        
        Print("=== DAILY LOSS LIMIT REACHED ===");
        Print("Limit: -$", DoubleToString(DailyLossLimit, 2), " | Current: $", DoubleToString(dailyProfitLoss, 2));
        
        // Close all positions
        if(CountOpenPositions() > 0)
            CloseAllPositions("Daily loss limit reached");
    }
}

//+------------------------------------------------------------------+
//| Calculate today's closed P/L from deal history                     |
//+------------------------------------------------------------------+
double CalculateTodaysClosedPL()
{
    double todayPL = 0;
    datetime todayStart = GetTradingDay();
    
    if(HistorySelect(todayStart, TimeCurrent()))
    {
        int totalDeals = HistoryDealsTotal();
        for(int i = 0; i < totalDeals; i++)
        {
            ulong ticket = HistoryDealGetTicket(i);
            if(ticket > 0)
            {
                if(HistoryDealGetInteger(ticket, DEAL_MAGIC) == MagicNumber &&
                   HistoryDealGetString(ticket, DEAL_SYMBOL) == _Symbol)
                {
                    ENUM_DEAL_ENTRY entry = (ENUM_DEAL_ENTRY)HistoryDealGetInteger(ticket, DEAL_ENTRY);
                    if(entry == DEAL_ENTRY_OUT || entry == DEAL_ENTRY_INOUT)
                    {
                        todayPL += HistoryDealGetDouble(ticket, DEAL_PROFIT);
                        todayPL += HistoryDealGetDouble(ticket, DEAL_SWAP);
                        todayPL += HistoryDealGetDouble(ticket, DEAL_COMMISSION);
                    }
                }
            }
        }
    }
    
    return todayPL;
}

//+------------------------------------------------------------------+
//| Detect best filling mode for the broker                            |
//+------------------------------------------------------------------+
ENUM_ORDER_TYPE_FILLING DetectFillingMode()
{
    if(!AutoDetectFilling)
        return ORDER_FILLING_FOK;
    
    int fillingModes = (int)SymbolInfoInteger(_Symbol, SYMBOL_FILLING_MODE);
    
    if((fillingModes & SYMBOL_FILLING_FOK) == SYMBOL_FILLING_FOK)
        return ORDER_FILLING_FOK;
    else if((fillingModes & SYMBOL_FILLING_IOC) == SYMBOL_FILLING_IOC)
        return ORDER_FILLING_IOC;
    else
        return ORDER_FILLING_RETURN;
}

//+------------------------------------------------------------------+
//| Get filling mode description                                       |
//+------------------------------------------------------------------+
string GetFillingModeDescription(ENUM_ORDER_TYPE_FILLING mode)
{
    switch(mode)
    {
        case ORDER_FILLING_FOK: return "FOK (Fill or Kill)";
        case ORDER_FILLING_IOC: return "IOC (Immediate or Cancel)";
        case ORDER_FILLING_RETURN: return "RETURN (Return mode)";
        default: return "Unknown";
    }
}
//+------------------------------------------------------------------+

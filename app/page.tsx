"use client";

import styles from "./page.module.css";
import axios from "axios";
import { useEffect, useState } from "react";
import { ChartComponent, EmaData, GraphData } from "../components";
import { RawData, getEma, parseData } from "../utils";
import { UTCTimestamp, Time } from "lightweight-charts";

const api = axios.create({
  baseURL: "./api",
});

const denyPolygon = false;

const timeFormatter = new Intl.DateTimeFormat("en-GB", { 
  year: "numeric",
  month: "numeric",
  day: "numeric",
  hour: "numeric",
  minute: "numeric",
  second: "numeric",
  hour12: false,
  // https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
  timeZone: "Europe/London"
});

export default function Home() {
  const [graphData, setGraphData] = useState<GraphData>([]);
  const [emaData, setEmaData] = useState<EmaData>([]);
  const [loading, setLoading] = useState(false);
  const [initialStock, setInitialStock] = useState(0);
  const [initialWallet, setInitialWallet] = useState(10000);
  const [money, setMoney] = useState(0);
  const [stock, setStock] = useState(0);
  const [wallet, setWallet] = useState(0);
  const [ticker, setTicker] = useState("AAPL");
  const [multiplier, setMultiplier] = useState(1);
  const [timespan, setTimespan] = useState("minute");
  const [from, setFrom] = useState("2024-03-07");
  const [to, setTo] = useState("2024-03-07");
  const [showEMA, setShowEMA] = useState(false);
  interface Trade {
    action: "BUY" | "SELL";
    price: number;
    amount: number;
    time: UTCTimestamp;
  }
  const [trades, setTrades] = useState<Trade[]>([]);

  useEffect(() => {
    updateGraph();
  }, []);

  function updateGraph() {
    setLoading(true);
    if (denyPolygon) {
      return;
    }
    api
      .get("/get_data", {
        params: {
          ticker,
          multiplier,
          timespan,
          from,
          to,
        },
      })
      .then((res) => {
        const json = res.data as RawData;
        const data = parseData(json);
        setGraphData(data);
        const ema = getEma(data, 10);
        setEmaData(ema);
      })
      .catch((err) => {
        console.error(err);
      })
      .finally(() => {
        setLoading(false);
      });
  }



  function simulate() {
    api
      .get("/simulate", {
        params: {
          initialStock,
          initialWallet,
          ticker,
          multiplier,
          timespan,
          from,
          to,
        },
      })
      .then((res) => {
        setTrades([]);
        const parsedData = res.data as [number, number][];
        for (let i = 0; i < parsedData.length; i++) {
          const [investedUnits, availableMoney] = parsedData[i];
          if (i !== 0) {
            const prevInvestedUnits = parsedData[i - 1][0];
            if (investedUnits !== prevInvestedUnits) {
              const unitDifference = investedUnits - prevInvestedUnits;
              const price = graphData[i].close;
              const time = graphData[i].time;
              if (unitDifference > 0) {
                setTrades((prev) => [...prev, {
                  action: "BUY",
                  price,
                  amount: unitDifference,
                  time,
                }])
              } else if (unitDifference < 0) {
                setTrades((prev) => [...prev, {
                  action: "SELL",
                  price,
                  amount: Math.abs(unitDifference),
                  time,
                }])
              } else {
                throw new Error("trade with zero value processed");
              }
            }
          }
        }
        // to get initial value, get initialStock * the first candlestick open + wallet
        const INITIAL_PRICE = graphData[0].open;
        const FINAL_PRICE = graphData[graphData.length - 1].close;
        const initialTotal = initialWallet + initialStock * INITIAL_PRICE;
        const finalWallet = parsedData[parsedData.length - 1][1];
        const finalTotal = finalWallet + parsedData[parsedData.length - 1][0] * FINAL_PRICE;
        const money = finalTotal - initialTotal;
        setMoney(money);



      })
      .catch((err) => {
        console.error(err);
      });
  }

  return (
    <main>
      <div className={styles.root}>
        <div className={styles.titleContainer}>
          <h1 className={styles.title}>trademaker</h1>
          <div
            className={`${styles.loadingBar} ${loading ? styles.loading : ""}`}
          ></div>
        </div>
        <ChartComponent data={graphData} ema={showEMA ? emaData : []} style={{ width: "75%" }} />
        <div className={styles.mainBody}>
          <div className={styles.tickerInput}>
            <input
              type="text"
              placeholder="Ticker"
              defaultValue="AAPL"
              onChange={(ev) => setTicker(ev.target.value)}
            />
            <input
              type="number"
              placeholder="Multiplier"
              defaultValue={1}
              onChange={(ev) => setMultiplier(+ev.target.value)}
            />
            <select onChange={(ev) => setTimespan(ev.target.value)}>
              selected={"minute"}
              <option value="minute">Minute</option>
              <option value="hour">Hour</option>
              <option value="day">Day</option>
            </select>
            <input 
              type="date" 
              onChange={(ev) => setFrom(ev.target.value)}
              defaultValue={"2023-03-07"} 
            />
            <input 
              type="date" 
              onChange={(ev) => setTo(ev.target.value)} 
              defaultValue={"2023-03-07"} 
            />

            <button
              onClick={() => {
                updateGraph();
              }}
            >
              Update
            </button>
            <label>
              <input type="checkbox" onChange={(ev) => setShowEMA(ev.target.checked)}/>
              <span>Show EMA</span>
            </label>
          </div>

          <div className={`${styles.interactionContainer} ${
            money > 0 
            ? styles.greenBox 
            : money < 0 
            ? styles.redBox 
            : ""}`
            }>
            <form
              className={styles.inputContainer}
              onSubmit={(event) => {
                event.preventDefault();
                simulate();
              }}
            >
              <label htmlFor="initialStock">
                
                <input
                  type="number"
                  placeholder="Initial money in stock"
                  defaultValue={0}
                  onChange={(ev) => setInitialStock(+ev.target.value)}
                />
              </label>

              <br />
              <label htmlFor="initialWallet">
                
                <input
                  type="number"
                  placeholder="Initial money in wallet"
                  defaultValue={10000}
                  onChange={(ev) => setInitialWallet(+ev.target.value)}
                />
              </label>

              <br />
              <input type="submit" value="Simulate" />
            </form>
            <div className={styles.output}>
              {/* <p>Number of stocks: {stock}</p> */}
              {/* <p>Money in wallet: £{wallet}</p> */}
              <p>Money difference: {money >= 0 ? "+£" + money.toFixed(2) : "-£" + (Math.abs(money)).toFixed(2)}</p>
              <p>Total money: £{(initialStock + initialWallet + money).toFixed(2)}</p>
            </div>
          </div>
          <div className={styles.tradelog}>
          <h2 className={styles.tradeTitle}>trade log</h2>
          {trades.map((trade) => (
            <div className={styles.trade}>
              <p>{timeFormatter.format(new Date(trade.time * 1000))}</p>
              <p>{trade.action} {(trade.amount).toFixed(2)} @ £{(trade.price).toFixed(2)}</p>
            </div>
          ))}
          </div>
        </div>
      </div>
    </main>
  );
}

"use client";

import styles from "./page.module.css";
import axios from "axios";
import { useEffect, useState } from "react";
import { ChartComponent, EmaData, GraphData } from "../components";
import { RawData, getEma, parseData } from "../utils";

const api = axios.create({
  baseURL: "./api",
});

const denyPolygon = false;

export default function Home() {
  const [graphData, setGraphData] = useState<GraphData>([]);
  const [emaData, setEmaData] = useState<EmaData>([]);
  const [loading, setLoading] = useState(false);
  const [initialStock, setInitialStock] = useState(0);
  const [initialWallet, setInitialWallet] = useState(0);
  const [money, setMoney] = useState(0);
  const [stock, setStock] = useState(0);
  const [wallet, setWallet] = useState(0);
  const [ticker, setTicker] = useState("AAPL");
  const [multiplier, setMultiplier] = useState(1);
  const [timespan, setTimespan] = useState("minute");
  const [from, setFrom] = useState("2023-01-03");
  const [to, setTo] = useState("2023-02-02");
  const [showEMA, setShowEMA] = useState(false);

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
        // ask boris to check this part
        const money = +res.data;
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
              onChange={(ev) => setTicker(ev.target.value)}
            />
            <input
              type="number"
              placeholder="Multiplier"
              onChange={(ev) => setMultiplier(+ev.target.value)}
            />
            <select onChange={(ev) => setTimespan(ev.target.value)}>
              <option value="minute">Minute</option>
              <option value="hour">Hour</option>
              <option value="day">Day</option>
            </select>
            <input type="date" onChange={(ev) => setFrom(ev.target.value)} />
            <input type="date" onChange={(ev) => setTo(ev.target.value)} />

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

          <div className={`${styles.interactionContainer} ${money > 0 
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
                  onChange={(ev) => setInitialStock(+ev.target.value)}
                />
              </label>

              <br />
              <label htmlFor="initialWallet">
                
                <input
                  type="number"
                  placeholder="Initial money in wallet"
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
        </div>
      </div>
    </main>
  );
}

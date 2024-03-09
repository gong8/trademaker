'use client'

import styles from "./page.module.css";
import axios from "axios";
import { useEffect,  useState } from "react";
import { ChartComponent, EmaData, GraphData } from "../components";
import { RawData, getEma, parseData } from "../utils";

const api = axios.create({
  baseURL: './api',
});

const denyPolygon = false;

export default function Home() {
  const [graphData, setGraphData] = useState<GraphData>([]);
  const [emaData, setEmaData] = useState<EmaData>([]);
  const [loading, setLoading] = useState(false);
  const [money, setMoney] = useState(0);
  const [stock, setStock] = useState(0);
  const [wallet, setWallet] = useState(0);

  useEffect(() => {
    setLoading(true);
    if (denyPolygon) {
      return;
    }
    const ticker = "AAPL";
    const multiplier = 1;
    const timespan = "minute";
    const from = "2023-01-03";
    const to = "2023-02-02";
    api.get("/get_data", {
      params: {
        ticker,
        multiplier,
        timespan,
        from,
        to,
      }
    }).then(res => {
      const json = res.data as RawData;
      const data = parseData(json);
      const ema = getEma(data, 10);
      setGraphData(data);
      setEmaData(ema);
    }).catch((err) => {
      console.error(err);
    }).finally(() => {
      setLoading(false);
    });
  }, []);

  return (
    <main>
      <div className={styles.root}>
        <div className={styles.titleContainer}>
          <h1 className={styles.title}>trademaker</h1>
          <div className={`${styles.loadingBar} ${loading ? styles.loading : ""}`}></div>
        </div>
        <ChartComponent data={graphData} style={{width: '75%'}} />
        <div className={styles.interactionContainer}>
          <form className={styles.inputContainer}>
            <label htmlFor="initialStock">
              £
            <input type="number" placeholder="Initial money in stock" />
            </label>
            
            <br/>
            <label htmlFor="initialWallet">
              £
              <input type="number" placeholder="Initial money in wallet" />
            </label>
            
            <br/>
            <input type="submit" value="Simulate"/>
          </form>
          <div className={styles.output}>
            <p>
              Number of stocks: {stock}
            </p>
            <p>
              Money in wallet: £{wallet}
            </p>
            <p>
              Total money: £{money}
            </p>
          </div>
        </div>  
      </div>
    </main>
  );
}

'use client'

import styles from "./page.module.css";
import axios from "axios";
import { useEffect,  useState } from "react";
import { ChartComponent, GraphData } from "../components";
import { RawData, parseData } from "../utils";

const api = axios.create({
  baseURL: './api',
});

const denyPolygon = false;

export default function Home() {
  const [graphData, setGraphData] = useState<GraphData>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    if (denyPolygon) {
      return;
    }
    const ticker = "AAPL";
    const multiplier = 1;
    const timespan = "hour";
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
      setGraphData(parseData(json));
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
      </div>
    </main>
  );
}

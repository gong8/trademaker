'use client'

import styles from "./page.module.css";
import axios from 'axios';
import dynamic from 'next/dynamic';
import { getNewOptions } from './graph'
import { useEffect,  useState } from 'react';

const CanvasJSChart = dynamic(
  async () => {
    const {
      default: CanvasJS
    } = await import('@canvasjs/react-charts');
    return CanvasJS.CanvasJSChart;
  },
  { ssr: false }
);

const api = axios.create({
  baseURL: './api',
});

const denyPolygon = false;

export default function Home() {
  const [data, setData] = useState<string | null>(null);
  const [options, setOptions] = useState<any>(null);
  const [graphData, setGraphData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    if (denyPolygon) {
      return;
    }
    const ticker = "AAPL";
    const multiplier = 1;
    const timespan = "day";
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
      console.info(res.data);
      setGraphData(res.data);
    }).catch((err) => {
      console.error(err);
    }).finally(() => {
      setLoading(false);
    });
  }, [])

  useEffect(() => {
    updateGraph(graphData);
  },[graphData])

  function updateGraph(data: any) {
    const newOptions = getNewOptions(data);
    setOptions(newOptions);
  }

  return (
    <main>
      <div className={styles.root}>
        <div className={styles.titleContainer}>
          <h1 className={styles.title}>trademaker</h1>
          <div className={`${styles.loadingBar} ${loading ? styles.loading : ""}`}></div>
        </div>

        <p className={styles.pythonTest}>{data}</p>
        {/*@ts-ignore*/}
        <CanvasJSChart options = {options} />
      </div>
    </main>
  );
}

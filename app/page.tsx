'use client'
import Image from "next/image";
import styles from "./page.module.css";
import axios from 'axios';
import { useEffect,  useState } from 'react';
import dynamic from 'next/dynamic';

const CanvasJSChart = dynamic(
  async () => {
    const {
      default: CanvasJS
    } = await import('@canvasjs/react-charts');
    return CanvasJS.CanvasJSChart;
  },
{ ssr: false }
);

const denyPolygon =  false;

const instance = axios.create(
  {
    baseURL: './api',
  },
)

const polygon = axios.create(
  {
    baseURL: 'https://api.polygon.io/v2/',
    headers: {'Authorization': process.env.APIKEY},
  }
)



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
    const indicesTicker = "AAPL";
    const multiplier = 10;
    const timespan = "minute";
    const from = "2023-01-03";
    const to = "2023-01-03";

    polygon.get(`aggs/ticker/${indicesTicker}/range/${multiplier}/${timespan}/${from}/${to}`).then((res) => {
      setGraphData(res.data);
    }).catch((err) => {
      console.log("error", err);
    }).finally(() => {
      setLoading(false);


    })

  }, [])


  useEffect(() => {
    updateGraph(graphData);
  },[graphData])

  function updateGraph(data: any) {
    let newDataPoints = [];
    if (data) {
      for (const dict of data.results) {
        // [Open, High, Low, Close]
        const [open, high, low, close] = [dict.o, dict.h, dict.l, dict.c]
        const time = new Date(dict.t);
        const point = {x: time, y: [open, high, low, close]};
        newDataPoints.push(point);
      }
    }
    setOptions({
      theme: "dark2",
      backgroundColor: "#000000",
      title: {
        text: ""
      },
      data: [{
        type: "candlestick",
        xValueFormatString: "MMM YYYY",
        yValueFormatString: "#,##0.00",
        dataPoints: newDataPoints,
      }]
    });
  }

  return (
    <main>
      <div className={styles.root}>
        <div className={styles.titleContainer}>
          <h1 className={styles.title}>trademaker</h1>
          <div className={`${styles.loadingBar} ${loading ? styles.loading : ""}`}></div>
        </div>

        <p>{data}</p>
        {/*@ts-ignore*/}
        <CanvasJSChart options = {options} />

      </div>
    </main>
  );
}

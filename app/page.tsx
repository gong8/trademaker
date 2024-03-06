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

const instance = axios.create(
  {baseURL: './api'}
)



export default function Home() {
  const [data, setData] = useState<string | null>(null)
  useEffect(() => {
    instance.get('/index')
      .then((response) => {
        setData(response.data);
      })
  })

  const options = {
    theme: "light2",
    title: {
      text: "Nifty 50 Index"
    },
    data: [{
      type: "line",
      xValueFormatString: "MMM YYYY",
      yValueFormatString: "#,##0.00",
      dataPoints: [{x: new Date(Date.now()), y: 0}]
    }]
  }

  return (
    <main>
      <h1>Home</h1>
      <p>{data}</p>
      {/*@ts-ignore*/}
      <CanvasJSChart options = {options} />
    </main>
  );
}

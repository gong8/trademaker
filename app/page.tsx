'use client'
import Image from "next/image";
import styles from "./page.module.css";
import axios from 'axios';
import { useEffect,  useState } from 'react';
import CanvasJSReact from '@canvasjs/react-charts';

const instance = axios.create(
  {baseURL: './api'}
)

const CanvasJS = CanvasJSReact.CanvasJS;
const CanvasJSChart = CanvasJSReact.CanvasJSChart;

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
      {/*<CanvasJSChart options = {options} />*/}
    </main>
  );
}

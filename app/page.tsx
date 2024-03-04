'use client'

import Image from 'next/image'
import Link from 'next/link'
import axios from 'axios'
import { useState, useEffect } from 'react'
// import * as CanvasJS from 'canvasjs';
// const CanvasJS = require('canvasjs');


const instance = axios.create(
  {baseURL: './api'}
)


export default function Home() {
  const [data, setData] = useState<string | null>(null);
  useEffect(() => {
    instance.get('/python').then((res) => {
      setData(res.data);
    }).catch((err) => {
      console.error(err);
    });
  }, []);
  return (
    <main>
      {data && <p>{data}</p>}
    </main>
  )
}

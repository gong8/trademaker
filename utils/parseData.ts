import { GraphData } from "@/components";
import { UTCTimestamp } from "lightweight-charts";

export interface RawData {
  results: {
    t: number;
    o: number;
    c: number;
    h: number;
    l: number;
  }[]
}

export function timestamp(date: Date): UTCTimestamp {
  return (date.getTime() / 1000) as UTCTimestamp;
}

export function parseData(data: RawData): GraphData {
  return data.results.map(({ t, o, c, h, l }) => ({ 
    time: timestamp(new Date(t)), 
    open: o, 
    high: h, 
    low: l, 
    close: c 
  }));
}
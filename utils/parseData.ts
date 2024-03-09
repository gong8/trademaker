import { EmaData, GraphData } from "@/components";
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

export function getEma(data: GraphData, width: number): EmaData {
  const smooth = 2 / (width + 1);
  let ema = 0;
  return data.map((val, i) => {
    if (i < width) {
      ema *= i;
      ema += val.close;
      ema /= (i + 1);
    } else {
      ema = val.close * smooth + ema * (1 - smooth);
    }
    return {
      time: val.time,
      value: ema
    };
  });
}
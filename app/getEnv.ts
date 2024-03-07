import * as dotenv from 'dotenv';
dotenv.config();

export function getAPIKEY() {
  console.log(process.env.APIKEY);
  return process.env.APIKEY;
}
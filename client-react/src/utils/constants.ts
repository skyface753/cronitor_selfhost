const apiPrefix = '/api/v1';
// No apiHost => Just apiPrefix
let apiHost = '';
if (process.env.NEXT_PUBLIC_DEV) {
  apiHost = 'http://localhost:8000';
}
export const API_URL = apiHost + apiPrefix;

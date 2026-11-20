export const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH ?? "/intent-mandate-guard";

export function withBase(path: string): string {
  if (!path) return BASE_PATH || "/";
  if (/^https?:\/\//i.test(path)) return path;
  const clean = path.startsWith("/") ? path : `/${path}`;
  return `${BASE_PATH}${clean}`;
}

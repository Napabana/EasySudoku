import type { PersistedSession } from "../types/sudoku";

const SESSION_KEY = "easysudoku.session.v1";
const IMAGE_DB = "easysudoku.images";
const IMAGE_STORE = "images";
const CURRENT_IMAGE_ID = "current";

function openImageDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(IMAGE_DB, 1);
    request.onupgradeneeded = () => {
      request.result.createObjectStore(IMAGE_STORE);
    };
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
  });
}

export function saveSession(session: PersistedSession): void {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

export function loadSession(): PersistedSession | null {
  const raw = localStorage.getItem(SESSION_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as PersistedSession;
  } catch {
    return null;
  }
}

export function clearSessionStorage(): void {
  localStorage.removeItem(SESSION_KEY);
}

export async function saveUploadedImage(file: File): Promise<void> {
  const db = await openImageDb();
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(IMAGE_STORE, "readwrite");
    tx.objectStore(IMAGE_STORE).put(file, CURRENT_IMAGE_ID);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
  db.close();
}

export async function loadUploadedImage(): Promise<Blob | null> {
  const db = await openImageDb();
  const blob = await new Promise<Blob | null>((resolve, reject) => {
    const tx = db.transaction(IMAGE_STORE, "readonly");
    const request = tx.objectStore(IMAGE_STORE).get(CURRENT_IMAGE_ID);
    request.onsuccess = () => resolve((request.result as Blob | undefined) ?? null);
    request.onerror = () => reject(request.error);
  });
  db.close();
  return blob;
}

export async function clearUploadedImage(): Promise<void> {
  const db = await openImageDb();
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(IMAGE_STORE, "readwrite");
    tx.objectStore(IMAGE_STORE).delete(CURRENT_IMAGE_ID);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
  db.close();
}

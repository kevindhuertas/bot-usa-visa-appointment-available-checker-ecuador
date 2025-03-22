'use client';

import * as React from 'react';
import { CacheProvider } from '@emotion/react';
import createEmotionCache from '@/createEmotionCache';

const clientSideEmotionCache = createEmotionCache();

interface EmotionProviderProps {
  children: React.ReactNode;
}

export default function EmotionProvider({ children }: EmotionProviderProps) {
  return <CacheProvider value={clientSideEmotionCache}>{children}</CacheProvider>;
}

/**
 * Progressive Web App Hooks
 * Ultra-high performance PWA features and offline capabilities
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useLocation } from 'react-router-dom';

// PWA Installation Interface
interface PWAInstallPrompt {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

// Network Status
interface NetworkStatus {
  isOnline: boolean;
  connectionType: string;
  effectiveType: string;
  downlink: number;
  rtt: number;
}

// Service Worker Status
interface ServiceWorkerStatus {
  isInstalled: boolean;
  isWaiting: boolean;
  isControlling: boolean;
  isUpdateAvailable: boolean;
  version?: string;
}

// Push Subscription
interface PushSubscriptionConfig {
  vapidKey: string;
  endpoint?: string;
}

// Cache Status
interface CacheStatus {
  totalSize: number;
  usageByCache: Record<string, number>;
  quota: number;
  usage: number;
}

/**
 * PWA Installation Hook
 */
export function usePWAInstall() {
  const [installPrompt, setInstallPrompt] = useState<PWAInstallPrompt | null>(null);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isStandalone, setIsStandalone] = useState(false);

  useEffect(() => {
    // Check if already installed
    setIsStandalone(
      window.matchMedia('(display-mode: standalone)').matches ||
      (window.navigator as any).standalone ||
      document.referrer.includes('android-app://')
    );

    // Listen for install prompt
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setInstallPrompt(e as any);
    };

    // Listen for app installed
    const handleAppInstalled = () => {
      setIsInstalled(true);
      setInstallPrompt(null);
      console.log('🎉 PWA installed successfully');
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const installPWA = useCallback(async () => {
    if (!installPrompt) return false;

    try {
      await installPrompt.prompt();
      const choiceResult = await installPrompt.userChoice;
      
      if (choiceResult.outcome === 'accepted') {
        console.log('✅ User accepted PWA installation');
        setIsInstalled(true);
        return true;
      } else {
        console.log('❌ User dismissed PWA installation');
        return false;
      }
    } catch (error) {
      console.error('Error during PWA installation:', error);
      return false;
    } finally {
      setInstallPrompt(null);
    }
  }, [installPrompt]);

  return {
    installPrompt: installPrompt !== null,
    isInstalled,
    isStandalone,
    installPWA,
    canInstall: installPrompt !== null && !isInstalled,
  };
}

/**
 * Network Status Hook
 */
export function useNetworkStatus() {
  const [networkStatus, setNetworkStatus] = useState<NetworkStatus>(() => {
    const connection = (navigator as any).connection;
    
    return {
      isOnline: navigator.onLine,
      connectionType: connection?.type || 'unknown',
      effectiveType: connection?.effectiveType || 'unknown',
      downlink: connection?.downlink || 0,
      rtt: connection?.rtt || 0,
    };
  });

  const [connectionHistory, setConnectionHistory] = useState<
    Array<{ status: 'online' | 'offline'; timestamp: number }>
  >([]);

  useEffect(() => {
    const updateNetworkStatus = () => {
      const connection = (navigator as any).connection;
      const isOnline = navigator.onLine;
      
      setNetworkStatus({
        isOnline,
        connectionType: connection?.type || 'unknown',
        effectiveType: connection?.effectiveType || 'unknown',
        downlink: connection?.downlink || 0,
        rtt: connection?.rtt || 0,
      });

      // Track connection history
      setConnectionHistory(prev => [
        ...prev.slice(-9), // Keep last 10 entries
        {
          status: isOnline ? 'online' : 'offline',
          timestamp: Date.now()
        }
      ]);
    };

    const handleOnline = () => {
      updateNetworkStatus();
      console.log('🌐 Network: Online');
    };

    const handleOffline = () => {
      updateNetworkStatus();
      console.log('📴 Network: Offline');
    };

    const handleConnectionChange = () => {
      updateNetworkStatus();
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Connection API events
    const connection = (navigator as any).connection;
    if (connection) {
      connection.addEventListener('change', handleConnectionChange);
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      if (connection) {
        connection.removeEventListener('change', handleConnectionChange);
      }
    };
  }, []);

  const getNetworkQuality = useCallback(() => {
    const { effectiveType, downlink, rtt } = networkStatus;
    
    if (!networkStatus.isOnline) return 'offline';
    if (effectiveType === '4g' && downlink > 1.5 && rtt < 150) return 'excellent';
    if (effectiveType === '4g' || (downlink > 0.8 && rtt < 300)) return 'good';
    if (effectiveType === '3g' || (downlink > 0.3 && rtt < 600)) return 'fair';
    return 'poor';
  }, [networkStatus]);

  return {
    ...networkStatus,
    connectionHistory,
    networkQuality: getNetworkQuality(),
  };
}

/**
 * Service Worker Hook
 */
export function useServiceWorker() {
  const [swStatus, setSwStatus] = useState<ServiceWorkerStatus>({
    isInstalled: false,
    isWaiting: false,
    isControlling: false,
    isUpdateAvailable: false,
  });

  const [updatePending, setUpdatePending] = useState(false);
  const swRegistration = useRef<ServiceWorkerRegistration | null>(null);

  useEffect(() => {
    if ('serviceWorker' in navigator) {
      registerServiceWorker();
    }
  }, []);

  const registerServiceWorker = useCallback(async () => {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js');
      swRegistration.current = registration;

      // Initial status
      setSwStatus(prev => ({
        ...prev,
        isInstalled: true,
        isControlling: registration.active !== null,
      }));

      // Listen for updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              setSwStatus(prev => ({ ...prev, isUpdateAvailable: true }));
              setUpdatePending(true);
              console.log('🆕 Service Worker update available');
            }
          });
        }
      });

      // Listen for controlling worker changes
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        setSwStatus(prev => ({ ...prev, isControlling: true }));
        window.location.reload();
      });

      // Listen for messages from SW
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data?.type === 'version') {
          setSwStatus(prev => ({ ...prev, version: event.data.version }));
        }
      });

      console.log('✅ Service Worker registered successfully');
    } catch (error) {
      console.error('❌ Service Worker registration failed:', error);
    }
  }, []);

  const updateServiceWorker = useCallback(async () => {
    if (swRegistration.current?.waiting) {
      swRegistration.current.waiting.postMessage({ type: 'SKIP_WAITING' });
      setUpdatePending(false);
      console.log('🔄 Service Worker update applied');
    }
  }, []);

  const unregisterServiceWorker = useCallback(async () => {
    if (swRegistration.current) {
      await swRegistration.current.unregister();
      setSwStatus({
        isInstalled: false,
        isWaiting: false,
        isControlling: false,
        isUpdateAvailable: false,
      });
      console.log('🗑️ Service Worker unregistered');
    }
  }, []);

  return {
    ...swStatus,
    updatePending,
    updateServiceWorker,
    unregisterServiceWorker,
    registration: swRegistration.current,
  };
}

/**
 * Push Notifications Hook
 */
export function usePushNotifications(config?: PushSubscriptionConfig) {
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [subscription, setSubscription] = useState<PushSubscription | null>(null);
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    setIsSupported('Notification' in window && 'serviceWorker' in navigator && 'PushManager' in window);
    setPermission(Notification.permission);
    
    if (isSupported) {
      getCurrentSubscription();
    }
  }, [isSupported]);

  const getCurrentSubscription = useCallback(async () => {
    try {
      const registration = await navigator.serviceWorker.getRegistration();
      if (registration) {
        const currentSubscription = await registration.pushManager.getSubscription();
        setSubscription(currentSubscription);
      }
    } catch (error) {
      console.error('Error getting push subscription:', error);
    }
  }, []);

  const requestPermission = useCallback(async (): Promise<boolean> => {
    if (!isSupported) return false;

    const result = await Notification.requestPermission();
    setPermission(result);
    
    if (result === 'granted') {
      console.log('✅ Push notification permission granted');
      return true;
    } else {
      console.log('❌ Push notification permission denied');
      return false;
    }
  }, [isSupported]);

  const subscribe = useCallback(async (): Promise<PushSubscription | null> => {
    if (!isSupported || permission !== 'granted' || !config?.vapidKey) {
      return null;
    }

    try {
      const registration = await navigator.serviceWorker.getRegistration();
      if (!registration) return null;

      const newSubscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: config.vapidKey,
      });

      setSubscription(newSubscription);
      console.log('✅ Push subscription created');
      
      return newSubscription;
    } catch (error) {
      console.error('Error creating push subscription:', error);
      return null;
    }
  }, [isSupported, permission, config]);

  const unsubscribe = useCallback(async (): Promise<boolean> => {
    if (!subscription) return false;

    try {
      await subscription.unsubscribe();
      setSubscription(null);
      console.log('🔕 Push subscription removed');
      return true;
    } catch (error) {
      console.error('Error removing push subscription:', error);
      return false;
    }
  }, [subscription]);

  const sendTestNotification = useCallback(async (title: string, body: string) => {
    if (permission !== 'granted') return false;

    try {
      new Notification(title, {
        body,
        icon: '/icon-192x192.png',
        badge: '/icon-72x72.png',
        vibrate: [200, 100, 200],
        tag: 'test-notification',
        renotify: true,
      });
      return true;
    } catch (error) {
      console.error('Error sending test notification:', error);
      return false;
    }
  }, [permission]);

  return {
    isSupported,
    permission,
    subscription,
    requestPermission,
    subscribe,
    unsubscribe,
    sendTestNotification,
    isSubscribed: subscription !== null,
  };
}

/**
 * Cache Management Hook
 */
export function useCacheManagement() {
  const [cacheStatus, setCacheStatus] = useState<CacheStatus | null>(null);
  const [loading, setLoading] = useState(false);

  const getCacheStatus = useCallback(async () => {
    setLoading(true);
    try {
      if ('storage' in navigator && 'estimate' in navigator.storage) {
        const estimate = await navigator.storage.estimate();
        const caches = await window.caches.keys();
        
        const usageByCache: Record<string, number> = {};
        
        for (const cacheName of caches) {
          const cache = await window.caches.open(cacheName);
          const keys = await cache.keys();
          let cacheSize = 0;
          
          for (const request of keys) {
            const response = await cache.match(request);
            if (response) {
              const blob = await response.blob();
              cacheSize += blob.size;
            }
          }
          
          usageByCache[cacheName] = cacheSize;
        }

        setCacheStatus({
          totalSize: Object.values(usageByCache).reduce((sum, size) => sum + size, 0),
          usageByCache,
          quota: estimate.quota || 0,
          usage: estimate.usage || 0,
        });
      }
    } catch (error) {
      console.error('Error getting cache status:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearCache = useCallback(async (cacheName?: string) => {
    try {
      if (cacheName) {
        await window.caches.delete(cacheName);
        console.log(`🗑️ Cache ${cacheName} cleared`);
      } else {
        const caches = await window.caches.keys();
        await Promise.all(caches.map(name => window.caches.delete(name)));
        console.log('🗑️ All caches cleared');
      }
      
      await getCacheStatus();
    } catch (error) {
      console.error('Error clearing cache:', error);
    }
  }, [getCacheStatus]);

  const preloadResources = useCallback(async (urls: string[]) => {
    try {
      const cache = await window.caches.open('preload-cache');
      await cache.addAll(urls);
      console.log(`📥 Preloaded ${urls.length} resources`);
      await getCacheStatus();
    } catch (error) {
      console.error('Error preloading resources:', error);
    }
  }, [getCacheStatus]);

  useEffect(() => {
    getCacheStatus();
  }, [getCacheStatus]);

  return {
    cacheStatus,
    loading,
    getCacheStatus,
    clearCache,
    preloadResources,
  };
}

/**
 * App Update Hook
 */
export function useAppUpdate() {
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const [updating, setUpdating] = useState(false);
  const { updateServiceWorker, updatePending } = useServiceWorker();

  useEffect(() => {
    setUpdateAvailable(updatePending);
  }, [updatePending]);

  const checkForUpdates = useCallback(async () => {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.getRegistration();
        await registration?.update();
      } catch (error) {
        console.error('Error checking for updates:', error);
      }
    }
  }, []);

  const applyUpdate = useCallback(async () => {
    setUpdating(true);
    try {
      await updateServiceWorker();
    } catch (error) {
      console.error('Error applying update:', error);
    } finally {
      setUpdating(false);
    }
  }, [updateServiceWorker]);

  return {
    updateAvailable,
    updating,
    checkForUpdates,
    applyUpdate,
  };
}

/**
 * Offline Data Sync Hook
 */
export function useOfflineSync() {
  const [pendingData, setPendingData] = useState<any[]>([]);
  const [syncing, setSyncing] = useState(false);
  const [lastSync, setLastSync] = useState<Date | null>(null);
  const { isOnline } = useNetworkStatus();

  const addPendingData = useCallback((data: any) => {
    const item = {
      id: `offline_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      data,
      timestamp: new Date().toISOString(),
      synced: false,
    };

    setPendingData(prev => [...prev, item]);
    
    // Store in IndexedDB
    try {
      const stored = localStorage.getItem('pendingOfflineData');
      const existing = stored ? JSON.parse(stored) : [];
      localStorage.setItem('pendingOfflineData', JSON.stringify([...existing, item]));
    } catch (error) {
      console.error('Error storing offline data:', error);
    }

    return item.id;
  }, []);

  const syncPendingData = useCallback(async (syncFunction: (data: any) => Promise<boolean>) => {
    if (!isOnline || syncing || pendingData.length === 0) return;

    setSyncing(true);
    const syncedIds: string[] = [];

    try {
      for (const item of pendingData) {
        if (!item.synced) {
          const success = await syncFunction(item.data);
          if (success) {
            syncedIds.push(item.id);
            item.synced = true;
            item.syncedAt = new Date().toISOString();
          }
        }
      }

      // Update state
      setPendingData(prev => prev.filter(item => !syncedIds.includes(item.id)));
      
      // Update localStorage
      const remaining = pendingData.filter(item => !syncedIds.includes(item.id));
      localStorage.setItem('pendingOfflineData', JSON.stringify(remaining));
      
      setLastSync(new Date());
      console.log(`✅ Synced ${syncedIds.length} offline items`);
      
    } catch (error) {
      console.error('Error syncing offline data:', error);
    } finally {
      setSyncing(false);
    }
  }, [isOnline, syncing, pendingData]);

  // Load pending data on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem('pendingOfflineData');
      if (stored) {
        const data = JSON.parse(stored);
        setPendingData(data.filter((item: any) => !item.synced));
      }
    } catch (error) {
      console.error('Error loading offline data:', error);
    }
  }, []);

  return {
    pendingData,
    syncing,
    lastSync,
    hasPendingData: pendingData.length > 0,
    addPendingData,
    syncPendingData,
  };
}

/**
 * PWA Share Hook
 */
export function usePWAShare() {
  const [canShare, setCanShare] = useState(false);

  useEffect(() => {
    setCanShare('share' in navigator);
  }, []);

  const share = useCallback(async (data: {
    title?: string;
    text?: string;
    url?: string;
    files?: File[];
  }) => {
    if (!canShare) return false;

    try {
      await (navigator as any).share(data);
      console.log('✅ Content shared successfully');
      return true;
    } catch (error) {
      if ((error as Error).name !== 'AbortError') {
        console.error('Error sharing content:', error);
      }
      return false;
    }
  }, [canShare]);

  return {
    canShare,
    share,
  };
}

/**
 * Combined PWA Hook
 */
export function usePWA(config?: { vapidKey?: string }) {
  const install = usePWAInstall();
  const network = useNetworkStatus();
  const serviceWorker = useServiceWorker();
  const pushNotifications = usePushNotifications(config);
  const cacheManagement = useCacheManagement();
  const appUpdate = useAppUpdate();
  const offlineSync = useOfflineSync();
  const share = usePWAShare();

  return {
    install,
    network,
    serviceWorker,
    pushNotifications,
    cacheManagement,
    appUpdate,
    offlineSync,
    share,
  };
}
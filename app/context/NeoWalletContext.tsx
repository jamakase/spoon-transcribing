'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Interface for the N3 provider based on documentation
interface NeoLineN3Provider {
  getAccount: () => Promise<{ address: string; label: string }>;
  // Add other methods if needed
}

interface NeoWalletContextType {
  address: string | null;
  isConnected: boolean;
  connect: () => Promise<void>;
  disconnect: () => void;
}

const NeoWalletContext = createContext<NeoWalletContextType>({
  address: null,
  isConnected: false,
  connect: async () => {},
  disconnect: () => {},
});

export function useNeoWallet() {
  return useContext(NeoWalletContext);
}

export function NeoWalletProvider({ children }: { children: ReactNode }) {
  const [address, setAddress] = useState<string | null>(null);
  const [neoLineN3, setNeoLineN3] = useState<NeoLineN3Provider | null>(null);

  useEffect(() => {
    // 1. Check for persistent session
    const savedAddress = localStorage.getItem('neo_wallet_address');
    if (savedAddress) {
      setAddress(savedAddress);
    }

    // 2. Initialization Logic based on Official Docs
    // https://tutorial.neoline.io/reference/neo3-provider-api
    
    const initN3 = () => {
      try {
        // @ts-ignore
        const n3 = new window.NEOLineN3.Init();
        if (n3) {
          setNeoLineN3(n3);
          console.log('NeoLine N3 Initialized Successfully');
          
          // Optionally listen for account changes or connection events
          window.addEventListener('NEOLine.NEO.EVENT.CONNECTED', (event: any) => {
             console.log('NeoLine Connected Event:', event.detail);
             if (event.detail && event.detail.address) {
               setAddress(event.detail.address);
               localStorage.setItem('neo_wallet_address', event.detail.address);
             }
          });
        }
      } catch (e) {
        console.log('NeoLineN3 not ready yet');
      }
    };

    // Listen for the N3 Ready event
    window.addEventListener('NEOLine.N3.EVENT.READY', initN3);

    // Also try immediately in case we missed the event
    if (typeof window !== 'undefined') {
       // @ts-ignore
       if (window.NEOLineN3) {
         initN3();
       }
    }

    return () => {
      window.removeEventListener('NEOLine.N3.EVENT.READY', initN3);
    };
  }, []);

  const connect = async () => {
    if (!neoLineN3) {
      // Fallback check if user just installed it or it loaded late
      // @ts-ignore
      if (window.NEOLineN3) {
         // @ts-ignore
         const n3 = new window.NEOLineN3.Init();
         setNeoLineN3(n3);
         try {
            const account = await n3.getAccount();
            if (account && account.address) {
              setAddress(account.address);
              localStorage.setItem('neo_wallet_address', account.address);
              return;
            }
         } catch (e) {
            console.error(e);
         }
      }

      window.open('https://chrome.google.com/webstore/detail/neoline/cphhlgmgameodnhkjdmkpanlelnlohao', '_blank');
      alert('NeoLine N3 wallet not detected. Please install the extension and reload.');
      return;
    }

    try {
      const account = await neoLineN3.getAccount();
      
      if (account && account.address) {
        setAddress(account.address);
        localStorage.setItem('neo_wallet_address', account.address);
      }
    } catch (error) {
      console.error('Failed to connect Neo wallet:', error);
      // NeoLine often throws if the user rejects or closes the popup
    }
  };

  const disconnect = () => {
    setAddress(null);
    localStorage.removeItem('neo_wallet_address');
  };

  return (
    <NeoWalletContext.Provider value={{ 
      address, 
      isConnected: !!address, 
      connect, 
      disconnect 
    }}>
      {children}
    </NeoWalletContext.Provider>
  );
}

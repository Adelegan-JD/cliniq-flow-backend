import { create } from 'zustand';

type State = { token: string | null; role: string | null; setAuth: (token: string, role: string) => void };
export const useUserStore = create<State>((set) => ({ token: null, role: null, setAuth: (token, role) => set({ token, role }) }));

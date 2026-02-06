import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";
import { contactsApi } from "./contactsApi";
import type { Contact, ContactCreate, ContactUpdate } from "./types";

interface ContactsState {
  contacts: Contact[];
  currentContact: Contact | null;
  loading: boolean;
  error: string | null;
  lastFetched: number | null;
}

interface ContactsActions {
  fetchContacts: () => Promise<void>;
  createContact: (data: ContactCreate) => Promise<void>;
  updateContact: (id: number, data: ContactUpdate) => Promise<void>;
  deleteContact: (id: number) => Promise<void>;
  setCurrentContact: (contact: Contact | null) => void;
  clearError: () => void;
}

type ContactsStore = ContactsState & ContactsActions;

const initialState: ContactsState = {
  contacts: [],
  currentContact: null,
  loading: false,
  error: null,
  lastFetched: null,
};

export const useContactStore = create<ContactsStore>()(
  devtools(
    persist(
      (set) => ({
        ...initialState,

        // ============================================
        // CRUD ACTIONS
        // ============================================
        fetchContacts: async () => {
          try {
            set({ loading: true, error: null });
            console.log("🔄 Fetching contacts...");

            const contacts = await contactsApi.getAll();
            console.log("✅ Contacts loaded:", contacts);

            set({
              contacts,
              loading: false,
              lastFetched: Date.now(),
            });
          } catch (error) {
            console.error("❌ Error fetching contacts:", error);
            const errorMessage =
              error instanceof Error
                ? error.message
                : "Error al cargar contactos";
            set({ error: errorMessage, loading: false });
          }
        },

        createContact: async (data: ContactCreate) => {
          try {
            set({ loading: true, error: null });
            console.log("🔄 Creating contact...");

            await contactsApi.create(data);
            console.log("✅ Contact created successfully");

            // Actualizar la lista de contactos
            const contacts = await contactsApi.getAll();
            set({
              contacts,
              loading: false,
            });
          } catch (error) {
            console.error("❌ Error creating contact:", error);
            const errorMessage =
              error instanceof Error
                ? error.message
                : "Error al crear contacto";
            set({ error: errorMessage, loading: false });
            throw error;
          }
        },

        updateContact: async (id: number, data: ContactUpdate) => {
          try {
            set({ loading: true, error: null });
            console.log(`🔄 Updating contact ${id}...`);

            await contactsApi.update(id, data);
            console.log(`✅ Contact ${id} updated successfully`);

            // Actualizar la lista de contactos
            const contacts = await contactsApi.getAll();
            set({
              contacts,
              loading: false,
            });
          } catch (error) {
            console.error(`❌ Error updating contact ${id}:`, error);
            const errorMessage =
              error instanceof Error
                ? error.message
                : "Error al actualizar contacto";
            set({ error: errorMessage, loading: false });
            throw error;
          }
        },

        deleteContact: async (id: number) => {
          try {
            set({ loading: true, error: null });
            console.log(`🔄 Deleting contact ${id}...`);

            await contactsApi.delete(id);
            console.log(`✅ Contact ${id} deleted successfully`);

            // Actualizar la lista de contactos
            const contacts = await contactsApi.getAll();
            set({
              contacts,
              loading: false,
            });
          } catch (error) {
            console.error(`❌ Error deleting contact ${id}:`, error);
            const errorMessage =
              error instanceof Error
                ? error.message
                : "Error al eliminar contacto";
            set({ error: errorMessage, loading: false });
            throw error;
          }
        },

        // ============================================
        // STATE MANAGEMENT
        // ============================================
        setCurrentContact: (contact) => {
          set({ currentContact: contact });
        },

        clearError: () => {
          set({ error: null });
        },
      }),
      {
        name: "contacts-store",
        partialize: (state) => ({
          contacts: state.contacts,
          currentContact: state.currentContact,
          lastFetched: state.lastFetched,
        }),
      },
    ),
    {
      name: 'contacts-store'
    }
  ),
);

// ============================================
// SELECTORS
// ============================================
export const useContacts = () => useContactStore((state) => state.contacts);
export const useContactLoading = () =>
  useContactStore((state) => state.loading);
export const useContactError = () => useContactStore((state) => state.error);
export const useCurrentContact = () =>
  useContactStore((state) => state.currentContact);

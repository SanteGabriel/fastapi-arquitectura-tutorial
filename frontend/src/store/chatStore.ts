import { create } from 'zustand';
import { Message, Conversation, ChatRequest, ChatResponse, LLMModel } from '@/types';
import axios from 'axios';

interface ChatState {
  messages: Message[];
  conversations: Conversation[];
  currentConversation: Conversation | null;
  availableModels: LLMModel[];
  selectedModel: string;
  isStreaming: boolean;
  isLoading: boolean;
  error: string | null;
}

interface ChatActions {
  sendMessage: (request: ChatRequest) => Promise<void>;
  loadConversations: () => Promise<void>;
  loadConversation: (id: string) => Promise<void>;
  createConversation: (title?: string) => Promise<string>;
  deleteConversation: (id: string) => Promise<void>;
  updateConversation: (id: string, updates: Partial<Conversation>) => Promise<void>;
  loadModels: () => Promise<void>;
  setSelectedModel: (model: string) => void;
  clearMessages: () => void;
  setError: (error: string | null) => void;
}

type ChatStore = ChatState & ChatActions;

const API_BASE_URL = process.env.NEXT_PUBLIC_CHAT_SERVICE_URL || 'http://localhost:8002';

export const useChatStore = create<ChatStore>((set, get) => ({
  // Initial state
  messages: [],
  conversations: [],
  currentConversation: null,
  availableModels: [],
  selectedModel: 'openai',
  isStreaming: false,
  isLoading: false,
  error: null,

  // Actions
  sendMessage: async (request: ChatRequest) => {
    try {
      set({ isLoading: true, error: null });

      // Add user message immediately
      const userMessage: Message = {
        id: Date.now().toString(),
        conversation_id: request.conversation_id || '',
        role: 'user',
        content: request.message,
        tokens_used: 0,
        cost_estimate: 0,
        timestamp: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, userMessage]
      }));

      const token = localStorage.getItem('auth-token');
      const response = await axios.post<ChatResponse>(`${API_BASE_URL}/chat`, request, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      // Add assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        conversation_id: response.data.conversation_id,
        role: 'assistant',
        content: response.data.message,
        model_used: response.data.model_used,
        tokens_used: response.data.tokens_used,
        cost_estimate: response.data.cost_estimate,
        timestamp: response.data.timestamp,
        processing_time: response.data.processing_time,
      };

      set((state) => ({
        messages: [...state.messages, assistantMessage],
        isLoading: false,
      }));

      // Update current conversation if needed
      if (response.data.conversation_id && !get().currentConversation) {
        await get().loadConversation(response.data.conversation_id);
      }

    } catch (error) {
      console.error('Send message error:', error);
      set({ 
        isLoading: false, 
        error: 'Failed to send message. Please try again.' 
      });
    }
  },

  loadConversations: async () => {
    try {
      const token = localStorage.getItem('auth-token');
      const response = await axios.get(`${API_BASE_URL}/conversations`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      set({ conversations: response.data });
    } catch (error) {
      console.error('Load conversations error:', error);
      set({ error: 'Failed to load conversations' });
    }
  },

  loadConversation: async (id: string) => {
    try {
      set({ isLoading: true });
      
      const token = localStorage.getItem('auth-token');
      const [conversationResponse, messagesResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/conversations/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_BASE_URL}/conversations/${id}/messages`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      set({
        currentConversation: conversationResponse.data,
        messages: messagesResponse.data,
        isLoading: false,
      });
    } catch (error) {
      console.error('Load conversation error:', error);
      set({ 
        error: 'Failed to load conversation',
        isLoading: false 
      });
    }
  },

  createConversation: async (title = 'New Conversation'): Promise<string> => {
    try {
      const token = localStorage.getItem('auth-token');
      const response = await axios.post(
        `${API_BASE_URL}/conversations`,
        { title },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const newConversation = response.data;
      
      set((state) => ({
        conversations: [newConversation, ...state.conversations],
        currentConversation: newConversation,
        messages: [],
      }));

      return newConversation.id;
    } catch (error) {
      console.error('Create conversation error:', error);
      set({ error: 'Failed to create conversation' });
      throw error;
    }
  },

  deleteConversation: async (id: string) => {
    try {
      const token = localStorage.getItem('auth-token');
      await axios.delete(`${API_BASE_URL}/conversations/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      set((state) => ({
        conversations: state.conversations.filter(conv => conv.id !== id),
        currentConversation: state.currentConversation?.id === id ? null : state.currentConversation,
        messages: state.currentConversation?.id === id ? [] : state.messages,
      }));
    } catch (error) {
      console.error('Delete conversation error:', error);
      set({ error: 'Failed to delete conversation' });
    }
  },

  updateConversation: async (id: string, updates: Partial<Conversation>) => {
    try {
      const token = localStorage.getItem('auth-token');
      const response = await axios.put(
        `${API_BASE_URL}/conversations/${id}`,
        updates,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      set((state) => ({
        conversations: state.conversations.map(conv => 
          conv.id === id ? { ...conv, ...response.data } : conv
        ),
        currentConversation: state.currentConversation?.id === id 
          ? { ...state.currentConversation, ...response.data }
          : state.currentConversation,
      }));
    } catch (error) {
      console.error('Update conversation error:', error);
      set({ error: 'Failed to update conversation' });
    }
  },

  loadModels: async () => {
    try {
      const token = localStorage.getItem('auth-token');
      const response = await axios.get(`${API_BASE_URL}/models`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      set({ availableModels: response.data });
    } catch (error) {
      console.error('Load models error:', error);
      set({ error: 'Failed to load models' });
    }
  },

  setSelectedModel: (model: string) => {
    set({ selectedModel: model });
  },

  clearMessages: () => {
    set({ messages: [], currentConversation: null });
  },

  setError: (error: string | null) => {
    set({ error });
  },
}));

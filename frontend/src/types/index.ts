export interface Book {
  id: string;
  title: string;
  author: string;
  isbn?: string;
  category_id?: number;
  cover_url?: string;
  ebook_url?: string;
  total_copies: number;
  available_copies: number;
  qr_code_url?: string;
  description?: string;
  created_at?: string;
}

export interface Category {
  id: number;
  name: string;
}

export interface Issue {
  id: string;
  book_id: string;
  user_id: string;
  issue_date: string;
  due_date: string;
  return_date?: string;
  status: 'issued' | 'returned' | 'overdue';
  fine_amount: number;
  fine_paid: boolean;
}

export interface QRScanResponse {
  success: boolean;
  message: string;
  issue?: Issue;
}
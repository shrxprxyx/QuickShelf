'use client';

import { useState, useEffect } from 'react';
import { useApiClient } from '@/lib/api-client';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Pencil, Trash2, Plus, Search } from 'lucide-react';
import { toast } from 'sonner';
import { Book, Category } from '@/types';

export default function BooksPage() {
  const api = useApiClient();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [books, setBooks] = useState<Book[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState(searchParams.get('q') || '');
  const [formOpen, setFormOpen] = useState(false);
  const [editingBook, setEditingBook] = useState<Book | null>(null);
  const [formData, setFormData] = useState<Partial<Book>>({});
  const [initialized, setInitialized] = useState(false);

  const loadBooks = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (search) params.append('q', search);
      const res = await api.get(`/api/v1/books?${params.toString()}`);
      setBooks(res.data);
    } catch (error) {
      toast.error('Failed to load books');
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const res = await api.get('/api/v1/categories');
      setCategories(res.data);
    } catch (error) {
      console.error('Failed to load categories');
    }
  };

  useEffect(() => {
    if (!initialized) {
      loadBooks();
      loadCategories();
      setInitialized(true);
    }
  }, [initialized]);

  const handleAddBook = async () => {
    if (!formData.title || !formData.author) {
      toast.error('Title and author are required');
      return;
    }

    try {
      await api.post('/api/v1/books', {
        ...formData,
        total_copies: formData.total_copies || 1,
      });
      toast.success('Book added');
      setFormOpen(false);
      setFormData({});
      loadBooks();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to add book');
    }
  };

  const handleEditBook = async () => {
    if (!editingBook?.id) return;

    try {
      await api.put(`/api/v1/books/${editingBook.id}`, formData);
      toast.success('Book updated');
      setFormOpen(false);
      setFormData({});
      setEditingBook(null);
      loadBooks();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update book');
    }
  };

  const handleDeleteBook = async (bookId: string) => {
    if (!confirm('Are you sure?')) return;

    try {
      await api.delete(`/api/v1/books/${bookId}`);
      toast.success('Book deleted');
      loadBooks();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to delete book');
    }
  };

  const handleEdit = (book: Book) => {
    setEditingBook(book);
    setFormData(book);
    setFormOpen(true);
  };

  const handleSearch = () => {
    const params = new URLSearchParams();
    if (search) params.append('q', search);
    router.push(`?${params.toString()}`);
    loadBooks();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Books Management</h1>
        <p className="text-muted-foreground">Manage your library's book collection</p>
      </div>

      {/* Search */}
      <div className="flex gap-2">
        <Input
          placeholder="Search by title, author, or ISBN..."
          value={search}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearch(e.target.value)}
          onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => {
            if (e.key === 'Enter') handleSearch();
          }}
          className="flex-1"
        />
        <Button onClick={handleSearch} size="icon" variant="outline">
          <Search className="h-4 w-4" />
        </Button>
        <Button
          onClick={() => {
            setFormData({});
            setEditingBook(null);
            setFormOpen(true);
          }}
          className="gap-2"
        >
          <Plus className="h-4 w-4" />
          Add Book
        </Button>
      </div>

      {/* Table */}
      <Card>
        <CardHeader>
          <CardTitle>Books ({books.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-muted-foreground">Loading...</p>
          ) : books.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No books found</p>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Title</TableHead>
                    <TableHead>Author</TableHead>
                    <TableHead>ISBN</TableHead>
                    <TableHead>Availability</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {books.map((book) => (
                    <TableRow key={book.id}>
                      <TableCell className="font-medium">{book.title}</TableCell>
                      <TableCell>{book.author}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {book.isbn || '—'}
                      </TableCell>
                      <TableCell>
                        <Badge variant={book.available_copies > 0 ? 'default' : 'secondary'}>
                          {book.available_copies}/{book.total_copies}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right gap-2 flex justify-end">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(book)}
                          className="gap-2"
                        >
                          <Pencil className="h-4 w-4" />
                          Edit
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDeleteBook(book.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Form Dialog */}
      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{editingBook ? 'Edit Book' : 'Add New Book'}</DialogTitle>
            <DialogDescription>
              {editingBook ? 'Update book details' : 'Add a new book to the library'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <Label>Title *</Label>
              <Input
                value={formData.title || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setFormData({ ...formData, title: e.target.value })
                }
                placeholder="Book title"
              />
            </div>

            <div>
              <Label>Author *</Label>
              <Input
                value={formData.author || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setFormData({ ...formData, author: e.target.value })
                }
                placeholder="Author name"
              />
            </div>

            <div>
              <Label>ISBN</Label>
              <Input
                value={formData.isbn || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setFormData({ ...formData, isbn: e.target.value })
                }
                placeholder="ISBN"
              />
            </div>

            <div>
              <Label>Category</Label>
              <Select
                value={formData.category_id?.toString() || ''}
                onValueChange={(v: string | null) => {
                  if (v) {
                    setFormData({ ...formData, category_id: parseInt(v) });
                  }
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((cat) => (
                    <SelectItem key={cat.id} value={cat.id.toString()}>
                      {cat.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Total Copies</Label>
              <Input
                type="number"
                min="1"
                value={formData.total_copies || 1}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setFormData({ ...formData, total_copies: parseInt(e.target.value) })
                }
              />
            </div>

            <div>
              <Label>Description</Label>
              <Textarea
                value={formData.description || ''}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                placeholder="Book description"
                rows={3}
              />
            </div>

            <Button onClick={editingBook ? handleEditBook : handleAddBook} className="w-full">
              {editingBook ? 'Update Book' : 'Add Book'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
'use client';

import { useState, useEffect } from 'react';
import { useApiClient } from '@/lib/api-client';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { BookOpen, Search } from 'lucide-react';
import { Book, Category } from '@/types';

export default function BrowsePage() {
  const api = useApiClient();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [books, setBooks] = useState<Book[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState(searchParams.get('q') || '');
  const [category, setCategory] = useState(searchParams.get('category') || '');
  const [initialized, setInitialized] = useState(false);

  const loadBooks = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (search) params.append('q', search);
      if (category) params.append('category', category);

      const res = await api.get(`/api/v1/books?${params.toString()}`);
      setBooks(res.data);
    } catch (error) {
      console.error('Failed to load books');
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
      loadCategories();
      setInitialized(true);
    }
    loadBooks();
  }, [search, category, initialized]);

  const handleSearch = () => {
    const params = new URLSearchParams();
    if (search) params.append('q', search);
    if (category) params.append('category', category);
    router.push(`?${params.toString()}`);
  };

  const handleCategoryChange = (value: string | null) => {
    const categoryValue = value || '';
    setCategory(categoryValue);
    const params = new URLSearchParams();
    if (search) params.append('q', search);
    if (categoryValue) params.append('category', categoryValue);
    router.push(`?${params.toString()}`);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Browse Books</h1>
        <p className="text-muted-foreground">Discover books in our collection</p>
      </div>

      {/* Search & Filter */}
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:gap-4">
        <div className="flex-1 flex gap-2">
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
        </div>

        <Select value={category} onValueChange={handleCategoryChange}>
          <SelectTrigger className="w-full md:w-40">
            <SelectValue placeholder="All Categories" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Categories</SelectItem>
            {categories.map((cat) => (
              <SelectItem key={cat.id} value={cat.id.toString()}>
                {cat.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Books Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {loading ? (
          <p className="col-span-full text-center text-muted-foreground">Loading...</p>
        ) : books.length === 0 ? (
          <p className="col-span-full text-center text-muted-foreground py-12">
            No books found
          </p>
        ) : (
          books.map((book) => (
            <Card key={book.id} className="flex flex-col h-full hover:shadow-lg transition-shadow">
              {book.cover_url && (
                <div className="w-full h-48 bg-muted overflow-hidden rounded-t-lg">
                  <img
                    src={book.cover_url}
                    alt={book.title}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}
              <CardHeader>
                <CardTitle className="text-lg line-clamp-2">{book.title}</CardTitle>
                <CardDescription>{book.author}</CardDescription>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col justify-between gap-4">
                <div className="space-y-2">
                  {book.isbn && (
                    <p className="text-xs text-muted-foreground">ISBN: {book.isbn}</p>
                  )}
                  {book.description && (
                    <p className="text-sm text-muted-foreground line-clamp-3">
                      {book.description}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Badge
                    variant={book.available_copies > 0 ? 'default' : 'secondary'}
                    className="w-full text-center justify-center"
                  >
                    {book.available_copies > 0
                      ? `${book.available_copies} Available`
                      : 'Not Available'}
                  </Badge>
                  {book.available_copies === 0 && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full gap-2"
                      onClick={() => {
                        // TODO: Implement reservation
                        console.log('Reserve:', book.id);
                      }}
                    >
                      <BookOpen className="h-4 w-4" />
                      Reserve
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
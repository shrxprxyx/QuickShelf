'use client';

import { useState, useRef, useEffect } from 'react';
import { useApiClient } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { Issue } from '@/types';

// @ts-ignore - html5-qrcode doesn't have proper types
import { Html5QrcodeScanner } from 'html5-qrcode';

export default function ScanPage() {
  const api = useApiClient();
  const [isScanning, setIsScanning] = useState(false);
  const [studentEmail, setStudentEmail] = useState('');
  const [issues, setIssues] = useState<Issue[]>([]);
  const scannerInstance = useRef<any>(null);

  const loadIssues = async () => {
    try {
      const res = await api.get('/api/issues');
      setIssues(res.data.slice(0, 10));
    } catch (error) {
      console.error('Failed to load issues');
    }
  };

  useEffect(() => {
    loadIssues();
    return () => {
      if (scannerInstance.current) {
        try {
          scannerInstance.current.clear();
        } catch (e) {}
      }
    };
  }, []);

  const startScanner = () => {
    if (!studentEmail.trim()) {
      toast.error('Please enter student email');
      return;
    }

    setIsScanning(true);

    // @ts-ignore
    const scanner = new Html5QrcodeScanner(
      'qr-reader',
      { fps: 10, qrbox: { width: 250, height: 250 } },
      false
    );

    scannerInstance.current = scanner;

    scanner.render(
      async (decodedText: string) => {
        if (decodedText.startsWith('book:')) {
          try {
            const res = await api.post('/api/issues/qr-scan', {
              qr_payload: decodedText,
              user_email: studentEmail,
            });
            toast.success(res.data.message);
            scanner.clear();
            setIsScanning(false);
            setStudentEmail('');
            loadIssues();
          } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Scan failed');
          }
        } else {
          toast.error('Invalid QR code');
        }
      },
      (error: any) => {}
    );
  };

  const stopScanner = () => {
    if (scannerInstance.current) {
      try {
        scannerInstance.current.clear();
      } catch (e) {}
    }
    setIsScanning(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">QR Scanner</h1>
        <p className="text-muted-foreground">Issue and return books using QR codes</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Scanner</CardTitle>
              <CardDescription>Scan book QR codes</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Student Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="student@example.com"
                  value={studentEmail}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setStudentEmail(e.target.value)}
                  disabled={isScanning}
                />
              </div>

              {isScanning ? (
                <>
                  <div
                    id="qr-reader"
                    className="w-full rounded-lg overflow-hidden border"
                    style={{ minHeight: '300px' }}
                  />
                  <Button onClick={stopScanner} variant="destructive" className="w-full">
                    Stop Scanner
                  </Button>
                </>
              ) : (
                <Button
                  onClick={startScanner}
                  className="w-full"
                  disabled={!studentEmail.trim()}
                >
                  Start Scanning
                </Button>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Last 10 scanned books</CardDescription>
            </CardHeader>
            <CardContent>
              {issues.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No activity yet</p>
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Book ID</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Date</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {issues.map((issue) => (
                        <TableRow key={issue.id}>
                          <TableCell className="font-mono text-xs">
                            {issue.book_id.slice(0, 8)}...
                          </TableCell>
                          <TableCell>
                            <Badge variant="default">{issue.status}</Badge>
                          </TableCell>
                          <TableCell className="text-xs text-muted-foreground">
                            {new Date(issue.issue_date).toLocaleDateString()}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
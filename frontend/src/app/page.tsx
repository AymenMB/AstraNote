'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Container, Typography, Box, Grid, Card, CardContent, Button } from '@mui/material';
import { Upload, Search, Document, BarChart } from '@mui/icons-material';
import { useAuthStore } from '@/store/authStore';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, user, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated || !user) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <Typography variant="h6">Loading...</Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h3" component="h1" gutterBottom>
          Welcome back, {user.full_name}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Your intelligent knowledge base powered by NotebookLM
        </Typography>
      </Box>

      {/* Quick Actions */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', cursor: 'pointer' }} onClick={() => router.push('/documents/upload')}>
            <CardContent sx={{ textAlign: 'center', p: 3 }}>
              <Upload color="primary" sx={{ fontSize: 48, mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Upload Documents
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Add new documents to your knowledge base
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', cursor: 'pointer' }} onClick={() => router.push('/query')}>
            <CardContent sx={{ textAlign: 'center', p: 3 }}>
              <Search color="primary" sx={{ fontSize: 48, mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Ask Questions
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Search your documents with AI-powered queries
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', cursor: 'pointer' }} onClick={() => router.push('/documents')}>
            <CardContent sx={{ textAlign: 'center', p: 3 }}>
              <Document color="primary" sx={{ fontSize: 48, mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Manage Documents
              </Typography>
              <Typography variant="body2" color="text.secondary">
                View and organize your document library
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', cursor: 'pointer' }} onClick={() => router.push('/analytics')}>
            <CardContent sx={{ textAlign: 'center', p: 3 }}>
              <BarChart color="primary" sx={{ fontSize: 48, mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Analytics
              </Typography>
              <Typography variant="body2" color="text.secondary">
                View usage statistics and insights
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Activity */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Queries
              </Typography>
              <Typography variant="body2" color="text.secondary">
                No recent queries. Start by asking a question!
              </Typography>
              <Box mt={2}>
                <Button variant="outlined" onClick={() => router.push('/query')}>
                  Ask Your First Question
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Document Library
              </Typography>
              <Typography variant="body2" color="text.secondary">
                No documents uploaded yet. Upload your first document to get started!
              </Typography>
              <Box mt={2}>
                <Button variant="outlined" onClick={() => router.push('/documents/upload')}>
                  Upload Your First Document
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}

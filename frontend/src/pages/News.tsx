import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  Chip,
  Link,
} from '@mui/material';
import waterFuturesAPI from '../services/api';

interface NewsItem {
  title: string;
  source: string;
  url: string;
  publishedAt: string;
  relevanceScore: number;
  sentimentScore: number;
  summary: string;
}

const News: React.FC = () => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNews();
  }, []);

  const fetchNews = async () => {
    try {
      const data = await waterFuturesAPI.getLatestNews(20);
      setNews(data);
    } catch (error) {
      console.error('Error fetching news:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (score: number) => {
    if (score > 0.2) return 'success';
    if (score < -0.2) return 'error';
    return 'warning';
  };

  const getSentimentLabel = (score: number) => {
    if (score > 0.2) return 'Positive';
    if (score < -0.2) return 'Negative';
    return 'Neutral';
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Water Market News
      </Typography>

      <Card>
        <CardContent>
          <List>
            {news.map((item, index) => (
              <ListItem key={index} alignItems="flex-start">
                <ListItemText
                  primary={
                    <Box>
                      <Link href={item.url} target="_blank" rel="noopener">
                        <Typography variant="subtitle1">
                          {item.title}
                        </Typography>
                      </Link>
                      <Box sx={{ mt: 1, mb: 1 }}>
                        <Chip 
                          label={item.source} 
                          size="small" 
                          sx={{ mr: 1 }}
                        />
                        <Chip 
                          label={getSentimentLabel(item.sentimentScore)} 
                          size="small" 
                          color={getSentimentColor(item.sentimentScore) as any}
                          sx={{ mr: 1 }}
                        />
                        <Chip 
                          label={`Relevance: ${(item.relevanceScore * 100).toFixed(0)}%`} 
                          size="small" 
                          variant="outlined"
                        />
                      </Box>
                    </Box>
                  }
                  secondary={
                    <>
                      <Typography variant="body2" paragraph>
                        {item.summary}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {new Date(item.publishedAt).toLocaleString()}
                      </Typography>
                    </>
                  }
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    </Box>
  );
};

export default News;
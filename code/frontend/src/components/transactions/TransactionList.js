// src/components/transactions/TransactionList.js
import React from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import { ArrowForward as ArrowForwardIcon } from '@mui/icons-material';

const TransactionList = ({ transactions }) => {
  return (
    <Card elevation={2} sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>Recent Transactions</Typography>
        
        <TableContainer component={Paper} variant="outlined" sx={{ mt: 2, mb: 2 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Merchant</TableCell>
                <TableCell align="right">Amount</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {transactions.map((transaction) => (
                <TableRow key={transaction.id}>
                  <TableCell>{transaction.timestamp}</TableCell>
                  <TableCell>{transaction.description}</TableCell>
                  <TableCell>{transaction.category}</TableCell>
                  <TableCell>{transaction.merchant}</TableCell>
                  <TableCell 
                    align="right"
                    sx={{ 
                      color: transaction.amount < 0 ? 'error.main' : 'success.main',
                      fontWeight: 'medium'
                    }}
                  >
                    {transaction.amount < 0 ? '-' : '+'}${Math.abs(transaction.amount).toFixed(2)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        
        {/* <Button 
          endIcon={<ArrowForwardIcon />}
          color="primary"
        >
          View all transactions
        </Button> */}
      </CardContent>
    </Card>
  );
};

export default TransactionList;
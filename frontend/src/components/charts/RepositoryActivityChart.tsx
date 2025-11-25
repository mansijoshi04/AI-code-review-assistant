/**
 * Bar chart showing repository activity statistics.
 */

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { RepositoryActivity } from '../../types'

interface RepositoryActivityChartProps {
  data: RepositoryActivity[]
  isLoading?: boolean
}

export function RepositoryActivityChart({
  data,
  isLoading,
}: RepositoryActivityChartProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Repository Activity</CardTitle>
        </CardHeader>
        <CardContent className="h-80 flex items-center justify-center">
          <div className="text-muted-foreground">Loading...</div>
        </CardContent>
      </Card>
    )
  }

  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Repository Activity</CardTitle>
        </CardHeader>
        <CardContent className="h-80 flex items-center justify-center">
          <div className="text-muted-foreground">No data available</div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Repository Activity</CardTitle>
      </CardHeader>
      <CardContent className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            layout="vertical"
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" tick={{ fontSize: 12 }} tickLine={false} />
            <YAxis
              type="category"
              dataKey="repository_name"
              tick={{ fontSize: 12 }}
              tickLine={false}
              width={150}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--background))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '8px',
              }}
            />
            <Legend />
            <Bar
              dataKey="review_count"
              fill="hsl(var(--primary))"
              name="Reviews"
            />
            <Bar
              dataKey="total_findings"
              fill="hsl(0 84.2% 60.2%)"
              name="Total Findings"
            />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

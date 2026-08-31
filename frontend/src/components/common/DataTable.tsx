import React from 'react';
import { colors, spacing, typography, borderRadius } from '../../tokens';

interface Column<T> {
  key: keyof T;
  label: string;
  render?: (value: any, row: T) => React.ReactNode;
  width?: string;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  className?: string;
  onRowClick?: (row: T) => void;
}

export function DataTable<T>({ data, columns, className = '', onRowClick }: DataTableProps<T>) {
  return (
    <div className={className} style={{ overflowX: 'auto' }}>
      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontFamily: typography.fontFamily.sans,
        }}
      >
        <thead>
          <tr
            style={{
              borderBottom: `2px solid ${colors.border.default}`,
            }}
          >
            {columns.map((column) => (
              <th
                key={String(column.key)}
                style={{
                  padding: spacing.md,
                  textAlign: 'left',
                  fontSize: typography.fontSize.sm,
                  fontWeight: typography.fontWeight.semibold as number,
                  color: colors.text.secondary,
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  width: column.width,
                }}
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIndex) => (
            <tr
              key={rowIndex}
              onClick={() => onRowClick?.(row)}
              style={{
                borderBottom: `1px solid ${colors.border.default}`,
                cursor: onRowClick ? 'pointer' : 'default',
                transition: 'background-color 0.15s ease',
              }}
              onMouseEnter={(e) => {
                if (onRowClick) {
                  e.currentTarget.style.backgroundColor = colors.background.tertiary;
                }
              }}
              onMouseLeave={(e) => {
                if (onRowClick) {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }
              }}
            >
              {columns.map((column) => (
                <td
                  key={String(column.key)}
                  style={{
                    padding: spacing.md,
                    fontSize: typography.fontSize.sm,
                    color: colors.text.primary,
                  }}
                >
                  {column.render
                    ? column.render(row[column.key], row)
                    : String(row[column.key] ?? '-')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {data.length === 0 && (
        <div
          style={{
            padding: spacing.xl,
            textAlign: 'center',
            color: colors.text.muted,
            fontSize: typography.fontSize.sm,
          }}
        >
          No data available
        </div>
      )}
    </div>
  );
}

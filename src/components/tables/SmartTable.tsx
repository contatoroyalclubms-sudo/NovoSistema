"use client"

import React, { useState, useMemo } from "react"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card"
import { 
  Search, 
  Filter, 
  Download, 
  ChevronUp, 
  ChevronDown, 
  MoreHorizontal,
  TrendingUp,
  TrendingDown,
  Star,
  Eye,
  Edit,
  Trash2
} from "lucide-react"

const customersData = [
  {
    id: 1,
    name: "Sérgio Miguel",
    email: "sergio@email.com",
    visits: 10,
    totalSpent: 1137,
    lastVisit: "2024-08-30",
    status: "VIP",
    trend: "up",
    category: "Premium"
  },
  {
    id: 2,
    name: "Ana Carolina",
    email: "ana@email.com",
    visits: 7,
    totalSpent: 892,
    lastVisit: "2024-08-29",
    status: "Regular",
    trend: "up",
    category: "Standard"
  },
  {
    id: 3,
    name: "Roberto Silva",
    email: "roberto@email.com",
    visits: 15,
    totalSpent: 2340,
    lastVisit: "2024-08-30",
    status: "VIP",
    trend: "down",
    category: "Premium"
  },
  {
    id: 4,
    name: "Maria Santos",
    email: "maria@email.com",
    visits: 3,
    totalSpent: 245,
    lastVisit: "2024-08-28",
    status: "New",
    trend: "up",
    category: "Basic"
  },
  {
    id: 5,
    name: "João Pedro",
    email: "joao@email.com",
    visits: 12,
    totalSpent: 1580,
    lastVisit: "2024-08-30",
    status: "Regular",
    trend: "up",
    category: "Standard"
  }
]

const productsData = [
  {
    id: 1,
    name: "Cerveja Artesanal IPA",
    category: "Cerveja",
    price: 18.50,
    stock: 45,
    sold: 127,
    revenue: 2349.50,
    trend: "up",
    rating: 4.8
  },
  {
    id: 2,
    name: "Whisky Premium",
    category: "Destilados",
    price: 85.00,
    stock: 12,
    sold: 23,
    revenue: 1955.00,
    trend: "up",
    rating: 4.9
  },
  {
    id: 3,
    name: "Vinho Tinto Reserva",
    category: "Vinhos",
    price: 45.00,
    stock: 28,
    sold: 34,
    revenue: 1530.00,
    trend: "down",
    rating: 4.6
  },
  {
    id: 4,
    name: "Energético Premium",
    category: "Energéticos",
    price: 8.50,
    stock: 89,
    sold: 156,
    revenue: 1326.00,
    trend: "up",
    rating: 4.2
  },
  {
    id: 5,
    name: "Refrigerante Artesanal",
    category: "Refrigerantes",
    price: 6.00,
    stock: 67,
    sold: 98,
    revenue: 588.00,
    trend: "up",
    rating: 4.1
  }
]

interface Column {
  key: string
  label: string
  sortable?: boolean
  filterable?: boolean
  type?: "text" | "number" | "currency" | "date" | "status" | "trend"
}

interface SmartTableProps {
  title: string
  data: any[]
  columns: Column[]
  searchable?: boolean
  exportable?: boolean
  className?: string
}

function SmartTable({ title, data, columns, searchable = true, exportable = true, className = "" }: SmartTableProps) {
  const [searchTerm, setSearchTerm] = useState("")
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: "asc" | "desc" } | null>(null)
  const [filterConfig, setFilterConfig] = useState<Record<string, string>>({})
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 5

  const filteredData = useMemo(() => {
    let filtered = data

    if (searchTerm) {
      filtered = filtered.filter(item =>
        Object.values(item).some(value =>
          value?.toString().toLowerCase().includes(searchTerm.toLowerCase())
        )
      )
    }

    Object.entries(filterConfig).forEach(([key, value]) => {
      if (value) {
        filtered = filtered.filter(item =>
          item[key]?.toString().toLowerCase().includes(value.toLowerCase())
        )
      }
    })

    return filtered
  }, [data, searchTerm, filterConfig])

  const sortedData = useMemo(() => {
    if (!sortConfig) return filteredData

    return [...filteredData].sort((a, b) => {
      const aValue = a[sortConfig.key]
      const bValue = b[sortConfig.key]

      if (aValue < bValue) return sortConfig.direction === "asc" ? -1 : 1
      if (aValue > bValue) return sortConfig.direction === "asc" ? 1 : -1
      return 0
    })
  }, [filteredData, sortConfig])

  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage
    return sortedData.slice(startIndex, startIndex + itemsPerPage)
  }, [sortedData, currentPage])

  const totalPages = Math.ceil(sortedData.length / itemsPerPage)

  const handleSort = (key: string) => {
    setSortConfig(current => ({
      key,
      direction: current?.key === key && current.direction === "asc" ? "desc" : "asc"
    }))
  }

  const handleExport = (format: "csv" | "excel" | "pdf") => {
    console.log(`Exporting ${title} as ${format}`)
    alert(`Exportando ${title} como ${format.toUpperCase()}...`)
  }

  const renderCellContent = (item: any, column: Column) => {
    const value = item[column.key]

    switch (column.type) {
      case "currency":
        return `R$ ${value?.toFixed(2)}`
      case "status":
        const statusColors = {
          VIP: "bg-purple-100 text-purple-800",
          Regular: "bg-blue-100 text-blue-800",
          New: "bg-green-100 text-green-800"
        }
        return (
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[value as keyof typeof statusColors] || "bg-gray-100 text-gray-800"}`}>
            {value}
          </span>
        )
      case "trend":
        return value === "up" ? (
          <TrendingUp className="h-4 w-4 text-green-600" />
        ) : (
          <TrendingDown className="h-4 w-4 text-red-600" />
        )
      default:
        return value
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={className}
    >
      <Card className="border-0 shadow-xl">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              📊 {title}
            </CardTitle>
            <div className="flex items-center gap-2">
              {exportable && (
                <div className="relative group">
                  <button className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors">
                    <Download className="h-4 w-4 text-gray-600" />
                  </button>
                  <div className="absolute right-0 top-full mt-2 bg-white rounded-lg shadow-lg border py-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                    <button
                      onClick={() => handleExport("csv")}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    >
                      Exportar CSV
                    </button>
                    <button
                      onClick={() => handleExport("excel")}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    >
                      Exportar Excel
                    </button>
                    <button
                      onClick={() => handleExport("pdf")}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    >
                      Exportar PDF
                    </button>
                  </div>
                </div>
              )}
              <button className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors">
                <Filter className="h-4 w-4 text-gray-600" />
              </button>
            </div>
          </div>

          {searchable && (
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Busca inteligente..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          )}
        </CardHeader>

        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  {columns.map((column) => (
                    <th
                      key={column.key}
                      className={`text-left py-3 px-4 font-medium text-gray-700 ${
                        column.sortable ? "cursor-pointer hover:bg-gray-50" : ""
                      }`}
                      onClick={() => column.sortable && handleSort(column.key)}
                    >
                      <div className="flex items-center gap-2">
                        {column.label}
                        {column.sortable && (
                          <div className="flex flex-col">
                            <ChevronUp
                              className={`h-3 w-3 ${
                                sortConfig?.key === column.key && sortConfig.direction === "asc"
                                  ? "text-blue-600"
                                  : "text-gray-400"
                              }`}
                            />
                            <ChevronDown
                              className={`h-3 w-3 -mt-1 ${
                                sortConfig?.key === column.key && sortConfig.direction === "desc"
                                  ? "text-blue-600"
                                  : "text-gray-400"
                              }`}
                            />
                          </div>
                        )}
                      </div>
                    </th>
                  ))}
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Ações</th>
                </tr>
              </thead>
              <tbody>
                {paginatedData.map((item, index) => (
                  <motion.tr
                    key={item.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                  >
                    {columns.map((column) => (
                      <td key={column.key} className="py-3 px-4">
                        {renderCellContent(item, column)}
                      </td>
                    ))}
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <button className="p-1 rounded hover:bg-gray-200 transition-colors">
                          <Eye className="h-4 w-4 text-gray-600" />
                        </button>
                        <button className="p-1 rounded hover:bg-gray-200 transition-colors">
                          <Edit className="h-4 w-4 text-gray-600" />
                        </button>
                        <button className="p-1 rounded hover:bg-gray-200 transition-colors">
                          <MoreHorizontal className="h-4 w-4 text-gray-600" />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-6">
            <div className="text-sm text-gray-600">
              Mostrando {(currentPage - 1) * itemsPerPage + 1} a{" "}
              {Math.min(currentPage * itemsPerPage, sortedData.length)} de {sortedData.length} resultados
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 rounded border border-gray-200 text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Anterior
              </button>
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  className={`px-3 py-1 rounded text-sm ${
                    currentPage === page
                      ? "bg-blue-600 text-white"
                      : "border border-gray-200 hover:bg-gray-50"
                  }`}
                >
                  {page}
                </button>
              ))}
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-1 rounded border border-gray-200 text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Próximo
              </button>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

export function CustomersTable() {
  const columns: Column[] = [
    { key: "name", label: "Nome", sortable: true, filterable: true, type: "text" },
    { key: "email", label: "Email", sortable: true, filterable: true, type: "text" },
    { key: "visits", label: "Visitas", sortable: true, type: "number" },
    { key: "totalSpent", label: "Total Gasto", sortable: true, type: "currency" },
    { key: "lastVisit", label: "Última Visita", sortable: true, type: "date" },
    { key: "status", label: "Status", sortable: true, filterable: true, type: "status" },
    { key: "trend", label: "Tendência", type: "trend" }
  ]

  return (
    <SmartTable
      title="Clientes VIP - Análise Inteligente"
      data={customersData}
      columns={columns}
      searchable={true}
      exportable={true}
    />
  )
}

export function ProductsTable() {
  const columns: Column[] = [
    { key: "name", label: "Produto", sortable: true, filterable: true, type: "text" },
    { key: "category", label: "Categoria", sortable: true, filterable: true, type: "text" },
    { key: "price", label: "Preço", sortable: true, type: "currency" },
    { key: "stock", label: "Estoque", sortable: true, type: "number" },
    { key: "sold", label: "Vendidos", sortable: true, type: "number" },
    { key: "revenue", label: "Revenue", sortable: true, type: "currency" },
    { key: "trend", label: "Tendência", type: "trend" }
  ]

  return (
    <SmartTable
      title="Top Produtos - Performance Detalhada"
      data={productsData}
      columns={columns}
      searchable={true}
      exportable={true}
    />
  )
}

export default SmartTable

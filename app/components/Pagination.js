import { ChevronLeft, ChevronRight } from 'lucide-react'

export default function Pagination({ currentPage, totalPages, onPageChange }) {
  const pages = []
  const maxVisible = 5

  let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2))
  let endPage = Math.min(totalPages, startPage + maxVisible - 1)

  if (endPage - startPage < maxVisible - 1) {
    startPage = Math.max(1, endPage - maxVisible + 1)
  }

  for (let i = startPage; i <= endPage; i++) {
    pages.push(i)
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', marginTop: '48px' }}>
      
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        style={{
          padding: '10px 16px',
          background: currentPage === 1 ? '#f8fafc' : 'white',
          border: '1.5px solid #e2e8f0',
          borderRadius: '10px',
          cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '13px',
          fontWeight: '600',
          color: currentPage === 1 ? '#cbd5e1' : '#475569',
          transition: 'all 0.15s',
        }}>
        <ChevronLeft size={14} />
        Previous
      </button>

      {startPage > 1 && (
        <>
          <button onClick={() => onPageChange(1)} style={{
            padding: '10px 14px', background: 'white',
            border: '1.5px solid #e2e8f0', borderRadius: '10px',
            cursor: 'pointer', fontSize: '13px', fontWeight: '600', color: '#475569',
          }}>
            1
          </button>
          {startPage > 2 && <span style={{ color: '#cbd5e1', fontSize: '13px' }}>...</span>}
        </>
      )}

      {pages.map(page => (
        <button key={page} onClick={() => onPageChange(page)} style={{
          padding: '10px 14px',
          background: page === currentPage ? '#4f46e5' : 'white',
          border: page === currentPage ? '1.5px solid #4f46e5' : '1.5px solid #e2e8f0',
          borderRadius: '10px', cursor: 'pointer',
          fontSize: '13px', fontWeight: '600',
          color: page === currentPage ? 'white' : '#475569',
          transition: 'all 0.15s',
        }}>
          {page}
        </button>
      ))}

      {endPage < totalPages && (
        <>
          {endPage < totalPages - 1 && <span style={{ color: '#cbd5e1', fontSize: '13px' }}>...</span>}
          <button onClick={() => onPageChange(totalPages)} style={{
            padding: '10px 14px', background: 'white',
            border: '1.5px solid #e2e8f0', borderRadius: '10px',
            cursor: 'pointer', fontSize: '13px', fontWeight: '600', color: '#475569',
          }}>
            {totalPages}
          </button>
        </>
      )}

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        style={{
          padding: '10px 16px',
          background: currentPage === totalPages ? '#f8fafc' : 'white',
          border: '1.5px solid #e2e8f0',
          borderRadius: '10px',
          cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '13px',
          fontWeight: '600',
          color: currentPage === totalPages ? '#cbd5e1' : '#475569',
          transition: 'all 0.15s',
        }}>
        Next
        <ChevronRight size={14} />
      </button>
    </div>
  )
}
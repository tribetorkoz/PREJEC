interface StatsWidgetProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: React.ReactNode
}

export default function StatsWidget({ title, value, subtitle, icon }: StatsWidgetProps) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-gray-500 text-sm font-medium mb-2">{title}</h3>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className="text-gray-400">
            {icon}
          </div>
        )}
      </div>
    </div>
  )
}

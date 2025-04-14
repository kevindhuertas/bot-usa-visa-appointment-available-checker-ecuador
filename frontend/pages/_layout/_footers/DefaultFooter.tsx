import React from 'react';
import Footer from '../../../layout/Footer/Footer';
import classNames from 'classnames';
import useDarkMode from '../../../hooks/useDarkMode';
import Popovers from '../../../components/bootstrap/Popovers';

const DefaultFooter = () => {
	const { darkModeStatus } = useDarkMode();

	return (
		<Footer>
			<div className='container-fluid'>
				<div className='row'>
					<div className='col'>
						<Popovers
							title='DefaultFooter.tsx'
							desc={<code>pages/_layout/_footers/DefaultFooter.tsx</code>}>
							Footer
						</Popovers>
						<code className='ps-3'>DefaultFooter.tsx</code>
					</div>
					<div className='col-auto'>
						<Popovers
							title='DefaultFooter.tsx'
							desc={<code>pages/_layout/_footers/DefaultFooter.tsx</code>}>
							Footer
						</Popovers>
						<code className='ps-3'>DefaultFooter.tsx</code>
					</div>
				</div>
			</div>
		</Footer>
	);
};

export default DefaultFooter;
